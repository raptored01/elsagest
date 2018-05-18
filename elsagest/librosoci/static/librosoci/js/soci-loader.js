import buildSocioTr from './build-socio-tr';
import buildConsigliereTr from './build-consigliere-tr';

const deltaScrollPx = 30;

export default class SociLoader {
  constructor() {
    this.init();
  }

  init() {
    this.cleanup();
    this.fetchSoci();
    this.fetchConsiglieri();
  }

  fetchSoci(empty) {
    $('.table-soci').each((index, table) => {
      const target = $(table).find('.lista-soci');
      if (empty) {
        $(target).empty();
      }
      const infiniteScroll = $(target).attr('data-infinite-scroll');
      SociLoader.addLoader(target);

      let scadenza = '';
      let first = '';
      const after = `after: "${this.state.lastItemId || ''}"`;
      const limit = $(target).attr('data-first');

      if (limit) {
        first = `first: ${parseInt(limit, 10)}`;
      }
      if ($(target).attr('data-scadenza')) {
        scadenza = 'scadenza: true';
      }

      const orderby = 'orderby: "cognome"';
      const settings = [first, scadenza, orderby, after].join(', ');
      const showSezione = $(table).find('.elsa-italia').val() === 'true';

      const query = `
        {
          allSoci(
            ${settings}
            ) {
            edges {
                node {
                  id
                  nome
                  cognome
                  numeroTessera
                  email
                  dataIscrizione
                  ultimoRinnovo
                  scadenzaIscrizione
                  promemoriaInviato
                  sezione{
                    nome
                  }
                }
              }
              pageInfo {
                startCursor
                endCursor
                hasNextPage
              }
            }
          }
      `;

      $.post({
        url: '/graphql/',
        data: JSON.stringify({ query }),
        contentType: 'application/json'
      })
        .done(response => {
          const { infiniteScrollInit } = this.state;
          const { pageInfo, edges } = response.data.allSoci;
          const { hasNextPage, endCursor } = pageInfo;

          // update local data structures with graphql help
          this.state.canFetchMore = hasNextPage;
          if (!scadenza) {
            this.state.lastItemId = endCursor || null;
          }

          SociLoader.removeLoader(target);
          if (edges.length > 0) {
            // populate panel with results
            const wrapper = $(target);
            edges.forEach(edge => {
              const item = buildSocioTr(edge.node, showSezione);
              wrapper.append(item);
            });

            if (scadenza) {
              $('#soci-in-scadenza h3 button').removeClass('hidden');
            }

            if (hasNextPage && scadenza) {
              $(table).append($('<a target="_blank" href="/librosoci" class="float-right">Vedi tutti</a>'));
            }

            // init infinite scroll
            if (!infiniteScrollInit && infiniteScroll) {
              this.state.infiniteScrollInit = true;
              this.state.infiniteScrollEnabled = true;
              this.initInfiniteScroll();
            }
            // enable infinite scroll again
            this.state.infiniteScrollEnabled = true;
          } else {
            // show 'no results' message
            $(target).append(
              $(
                `
                <div class="no-results">
                  <p>Ottimo, nessun socio in scadenza!</p>
                </div>
                `
              )
            );
          }
        })
        .fail(() => {
          SociLoader.removeLoader(target);
          this.handleError();
        })
        .always(() => {
          SociLoader.removeLoader(target);
        });
    });
  }

  fetchConsiglieri() {
    $('.table-consiglio-direttivo').each((index, table) => {
      const target = $(table).find('.lista-consiglieri');
      $(target).empty();
      SociLoader.addLoader(target);
      const query = `
        {
          allSoci(consiglieri: true){
            edges{
              node{
                id
                nome
                cognome
                ruolo{
                  ruolo
                }
                consigliereDal
                emailconsigliere{
                  email
                }
              }
            }
          }
        }
      `;

      $.post({
        url: '/graphql/',
        data: JSON.stringify({ query }),
        contentType: 'application/json'
      })
        .done(response => {
          const { edges } = response.data.allSoci;
          if (edges.length > 0) {
            // populate panel with results
            const wrapper = $(target);
            edges.forEach(edge => {
              const item = buildConsigliereTr(edge.node);
              wrapper.append(item);
            });
          } else {
            // show 'no results' message
            $(target).append(
              $(
                `
                <div class="no-results">
                  <p>Ooops, nessun consigliere trovato!</p>
                </div>
                `
              )
            );
          }
        })
        .fail(() => {
          this.handleError();
        })
        .always(() => {
          SociLoader.removeLoader(target);
        });
    });
  }

  initInfiniteScroll() {
    $(window).scroll(() => {
      const { infiniteScrollEnabled, canFetchMore } = this.state;
      if (
        infiniteScrollEnabled &&
        canFetchMore &&
        ($(window).scrollTop() + $(window).height() > $(document).height() - deltaScrollPx)
      ) {
        // fetch additional items
        this.state.infiniteScrollEnabled = false;
        this.fetchSoci(false);
      }
    });
  }

  handleError() {
    // prevent infinite scroll from triggering
    this.state.infiniteScrollEnabled = false;
  }

  static addLoader(target) {
    $(target).append(
      $(
        `
        <div class="loader">
          <i class="fa fa-spinner fa-spin fa-3x fa-fw"></i>
        </div>
        `
      )
    );
  }

  static removeLoader(target) {
    $(target)
      .find('.loader')
      .remove();
  }

  cleanup() {
    this.state = {
      infiniteScrollInit: false,
      infiniteScrollEnabled: false,
      lastItemId: null,
      canFetchMore: false
    };
  }
}
