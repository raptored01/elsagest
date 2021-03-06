from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from datetime import date, timedelta
from django.utils import timezone
import re


# Create your models here.


class SezioneElsa(models.Model):
    nome = models.TextField()
    history = HistoricalRecords()

    @property
    def domain(self):
        domain = re.sub(r"[,']", r"", "".join(f"elsa{self.nome}".lower().split()))
        par = re.search('\((.+)\)', domain)
        if par:
            domain = "elsa" + par.group(1)
        return domain.lower()

    @property
    def denominazione(self):
        par = re.search('\((.+)\)', self.nome)
        if par:
            return par.group(1)
        else:
            return self.nome

    class Meta:
        db_table = "sezioni_elsa"
        verbose_name = "Sezione ELSA"
        verbose_name_plural = "Sezioni ELSA"

    def __str__(self):
        return f"ELSA {self.nome}"


class SociManager(models.Manager):

    def in_scadenza(self):
        return self.get_queryset().filter(scadenza_iscrizione__lte=date.today() + timedelta(days=15))

    def scaduto(self):
        return self.get_queryset().filter(scadenza_iscrizione__lte=date.today())


class Socio(models.Model):
    nome = models.TextField()
    cognome = models.TextField()
    sezione = models.ForeignKey(SezioneElsa, on_delete=models.CASCADE)
    numero_tessera = models.IntegerField()
    codice_fiscale = models.TextField()
    cellulare = models.TextField(null=True, blank=True, default="")
    email = models.EmailField()
    universita = models.TextField(null=True, blank=True, default="")
    data_iscrizione = models.DateField()
    quota_iscrizione = models.FloatField()
    scadenza_iscrizione = models.DateField()
    ultimo_rinnovo = models.DateField(auto_now_add=True)
    attivo = models.BooleanField(default=True)
    data_creazione = models.DateTimeField(auto_now_add=True)
    subscribed = models.BooleanField(default=True)
    history = HistoricalRecords()
    objects = SociManager()

    @property
    def scaduto(self):
        return self.scadenza_iscrizione < date.today()

    @property
    def promemoria_inviato(self):
        return Reminder.objects.filter(destinatari=self) and Reminder.objects.filter(destinatari=self).last().recent

    @property
    def iscritto_il(self):
        return self.data_iscrizione.strftime("%d-%m-%Y")

    @property
    def scade_il(self):
        return self.scadenza_iscrizione.strftime("%d-%m-%Y")

    @property
    def rinnovato_il(self):
        return self.ultimo_rinnovo.strftime("%d-%m-%Y")

    @property
    def nome_esteso(self):
        return f"{self.nome} {self.cognome}"

    def unsubscribe(self):
        self.subscribed = False
        self.unsubscribetoken.delete()
        self.save()

    class Meta:
        db_table = "soci"
        verbose_name = "Socio"
        verbose_name_plural = "Soci"


class Ruolo(models.Model):
    ruolo = models.TextField()
    abbreviazione = models.TextField()
    soci = models.ManyToManyField(Socio, through="Consigliere", related_name="ruolo_socio")

    class Meta:
        db_table = "ruoli_consiglieri"
        verbose_name = "Consigliere"
        verbose_name_plural = "Consiglieri"


class Consigliere(models.Model):
    ruolo = models.ForeignKey(Ruolo, on_delete=models.CASCADE)
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    sezione = models.ForeignKey(SezioneElsa, on_delete=models.CASCADE)
    consigliere_dal = models.DateField(auto_now_add=True)
    email = models.EmailField()
    history = HistoricalRecords()

    @property
    def in_carica_dal(self):
        return self.consigliere_dal.strftime("%d-%m-%Y")

    class Meta:
        db_table = "consiglieri"
        verbose_name = "Consigliere"
        verbose_name_plural = "Consiglieri"


class RinnovoIscrizione(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.DO_NOTHING)
    data_rinnovo = models.DateField()
    quota_rinnovo = models.FloatField()
    history = HistoricalRecords()

    class Meta:
        db_table = "rinnovi"
        verbose_name = "Rinnovo iscrizione"
        verbose_name_plural = "Rinnovi iscrizioni"


class ReminderManager(models.Manager):

    def last(self):
        return self.get_queryset().orderby('-inviata_il')


class Reminder(models.Model):
    mittente = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="reminder")
    destinatari = models.ManyToManyField(Socio, related_name="remaindee")
    inviata_il = models.DateTimeField(auto_now_add=True)

    @property
    def recent(self):
        return (timezone.now() - self.inviata_il).days < 15

    @property
    def not_recent(self):
        return (timezone.now() - self.inviata_il).days > 15
