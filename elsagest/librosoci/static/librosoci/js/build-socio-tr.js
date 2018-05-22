import moment from 'moment';
import config from './config';

export default (socio, showSezione) => {
  const tr = $(`<tr>
            <input type="hidden" class="id" value="${socio.id}">
            <td class="cognome">${socio.cognome}</td>
            <td class="nome">${socio.nome}</td>
            <td class="numero-tessera">${socio.numeroTessera}</td>
            <td class="email">${socio.email}</td>
            <td class="cellulare">${socio.cellulare}</td>
            <td class="universita">${socio.universita}</td>
            <td class="data-iscrizione">${socio.dataIscrizione.split('-').reverse().join('-')}</td>
            <td class="ultimo-rinnovo">${socio.ultimoRinnovo.split('-').reverse().join('-')}</td>
            <td class="scadenza-iscrizione">${socio.scadenzaIscrizione.split('-').reverse().join('-')}</td>
        </tr>`);
  if (showSezione) {
    $(tr).append(`<td class="sezione">${socio.sezione.denominazione}</td>`);
    $(tr).find('.ultimo-rinnovo').remove();
  }
  const scadenza = moment(socio.scadenzaIscrizione, config.MOMENT_DATE_FORMAT);
  if (scadenza.isBefore(moment())) {
    $(tr).find('.scadenza-iscrizione')
      .addClass('danger')
      .attr('title', 'Iscrizione scaduta');
  }
  if (socio.promemoriaInviato) {
    $(tr).find('.email')
      .addClass('bg-info')
      .attr('title', 'Promemoria inviato');
  }
  return tr;
};
