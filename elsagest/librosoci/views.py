from django.shortcuts import render
from django.http import JsonResponse
from graphql_relay.node.node import from_global_id
from .models import Socio, RinnovoIscrizione
from .random_pop import genera_sezioni
from datetime import date, datetime, timedelta
from django.shortcuts import redirect
from librosoci.models import SezioneElsa, Consigliere, Socio, Ruolo

# Create your views here.


def view(request):

    context = {
        "sezione": request.user.userprofile.sezione,
        "user": request.user,
        "sezioni": SezioneElsa.objects.exclude(nome="Nessuna")
    }

    return render(request, 'librosoci/libro_soci.html', context)


def aggiungi_socio(request):
    if request.method == "POST":
        try:
            post = request.POST
            print(post)
            data_iscrizione = datetime.strptime(post.get("data_iscrizione"), "%d-%m-%Y").date()
            scadenza_iscrizione = data_iscrizione + timedelta(days=364)
            sezione = request.user.userprofile.sezione
            print(sezione)
            socio = Socio.objects.create(
                nome=post.get("nome"),
                cognome=post.get("cognome"),
                codice_fiscale=post.get("codice_fiscale"),
                email=post.get("email"),
                numero_tessera=post.get("numero_tessera"),
                data_iscrizione=data_iscrizione,
                scadenza_iscrizione=scadenza_iscrizione,
                quota_iscrizione=post.get("quota_iscrizione"),
                cellulare=post.get("cellulare"),
                universita=post.get("univerisita"),
                sezione=sezione
            )
            socio.save()
            print("Everything ok!")
            return JsonResponse({"success": True})
        except Exception as e:
            raise
            print("Something went wrong!")
            #return JsonResponse({"success": False, "message": str(e)})
            raise


def modifica_socio(request):
    if request.method == "POST":
        try:
            user = request.user
            post = request.POST
            socio_id = from_global_id(post.get("id"))[1]
            socio = Socio.objects.get(pk=socio_id)
            if socio.sezione != user.userprofile.sezione:
                return JsonResponse({"success": False, "message": "Non puoi modificare soci diversi dalla tua sezione!"})
            elimina = post.get("elimina") == "delete"
            if elimina:
                socio.delete()
                return JsonResponse({"success": True, "message": "Socio eliminato"})
            try:
                data_iscrizione = datetime.strptime(post.get("data_iscrizione"), "%d-%m-%Y").date()
            except:
                data_iscrizione = datetime.strptime(post.get("data_iscrizione"), "%Y-%m-%d").date()

            scadenza_iscrizione = data_iscrizione + timedelta(days=364)
            socio.nome = post.get("nome")
            socio.cognome = post.get("cognome")
            socio.codice_fiscale = post.get("codice_fiscale")
            socio.email = post.get("email")
            socio.numero_tessera = post.get("numero_tessera")
            socio.data_iscrizione = data_iscrizione
            socio.scadenza_iscrizione = scadenza_iscrizione
            socio.cellulare = post.get("cellulare")
            socio.universita = post.get("universita")
            data_nuovo_rinnovo = post.get("data_nuovo_rinnovo")
            quota_nuovo_rinnovo = post.get("quota_nuovo_rinnovo")

            if data_nuovo_rinnovo and not quota_nuovo_rinnovo:
                return JsonResponse({"success": False, "message": "Specificare la quota di rinnovo"})
            elif quota_nuovo_rinnovo and not data_nuovo_rinnovo:
                return JsonResponse({"success": False, "message": "Specificare la data di rinnovo"})
            elif quota_nuovo_rinnovo and data_nuovo_rinnovo:
                data_rinnovo = datetime.strptime(data_nuovo_rinnovo, "%d-%m-%Y").date()
                scadenza_iscrizione = data_rinnovo + timedelta(days=364)
                socio.scadenza_iscrizione = scadenza_iscrizione
                rinnovo = RinnovoIscrizione.objects.create(data_rinnovo=data_rinnovo, quota_rinnovo=quota_nuovo_rinnovo,
                                                           socio=socio)
                rinnovo.save()
            socio.save()
            return JsonResponse({"success": True, "message": "Modifiche salvate!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Si è verificato un errore: {e}"})


ruoli_non_duplicabili = list(range(14, 20))  # tutti eccetto i Director


def modifica_consiglio(request):
    if request.method == "POST":
        user = request.user
        post = request.POST
        sezione_id = int(post.get("sezione"))
        sezione = SezioneElsa.objects.get(pk=sezione_id)

        if user.userprofile.sezione.id != sezione_id and not user.is_superuser:
            return JsonResponse({"success": False, "message": "Non hai i permessi per modificare questo consiglio"})

        # thanks to https://stackoverflow.com/a/5711993/3782345
        data_list = post.getlist("ruolo")
        new_roles = zip(*[data_list[i::4] for i in range(4)])
        if sezione.nome == "Italia":
            Consigliere.objects.filter(ruolo_id__in=range(1, 14)).delete()
        else:
            Consigliere.objects.filter(sezione=sezione).exclude(ruolo_id__in=range(1, 14)).delete()  # non eliminiamo i consiglieri nazionali
        ruoli_rimossi = []

        ruoli_assegnati = []
        for ruolo, id_socio, email, data in new_roles:
            try:
                id_ruolo = int(ruolo)
            except ValueError:
                id_ruolo = from_global_id(ruolo)[1]
            if id_ruolo in ruoli_assegnati and id_ruolo in ruoli_non_duplicabili:
                return {"success": False, "message": f"Non può esserci più di un {Ruolo.objects.get(pk=id_ruolo).ruolo}"}
            else:
                ruoli_assegnati.append(id_ruolo)
            if sezione.nome == "Italia":
                id_ruolo -= 13
            id_socio = from_global_id(id_socio)[1]
            socio = Socio.objects.get(pk=id_socio)
            ruolo = Ruolo.objects.get(pk=id_ruolo)
            consigliere_dal = datetime.strptime(data, "%d-%m-%Y").date()
            try:
                if sezione.nome == "Italia":
                    print("ELSA Italia")
                    ruoli_precedenti = Consigliere.objects.filter(socio=socio)  # abbiamo già eliminato tutti gli altri, non occorrono altri filtri
                    print(ruoli_precedenti)
                    if ruoli_precedenti:
                        for r in ruoli_precedenti:
                            ruoli_rimossi.append(f"{socio.nome_esteso} da {r.ruolo.ruolo} di ELSA {socio.sezione.nome}")
                            r.delete()
                    nuovo_ruolo = Consigliere.objects.create(
                        ruolo=ruolo,
                        socio=socio,
                        email=email,
                        sezione=sezione,
                        consigliere_dal=consigliere_dal
                    )
                    nuovo_ruolo.save()
                else:
                    ruolo_precedente = Consigliere.objects.get(socio=socio)  # quindi se è consigliere di ELSA Italia
                    return JsonResponse({"success": False, "message": f"{socio.nome_esteso} è già {ruolo_precedente.ruolo.ruolo}"})
            except:
                nuovo_ruolo = Consigliere.objects.create(ruolo=ruolo, socio=socio, sezione=sezione, email=email, consigliere_dal=consigliere_dal)
                nuovo_ruolo.save()

        message = f"Componenti del consiglio direttivo di ELSA {sezione.nome} aggiornati!"
        if ruoli_rimossi:
            message += ". I seguenti ruoli sono stati rimossi: " + "; ".join(ruoli_rimossi)
        return JsonResponse({"success": True, "message": message})


def popola_db(request):
    if request.method == "POST":
        genera_sezioni()
        print("database generato")
        return redirect("/")
