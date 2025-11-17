from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        risultati = []
        for impianti in self._impianti:
            consumi= impianti.get_consumi()
            consumi_mese = []
            for consumo in consumi:
                if consumo.data.month == mese and consumo.data.year == 2026:
                    consumi_mese.append(consumo.kwh)
            if len(consumi_mese) > 0:
                media = sum(consumi_mese) / len(consumi_mese)
                risultati.append((impianti.nome, media))
            else:
                risultati.append((impianti.nome, 0))
        return risultati






    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        if giorno == 8:
            if costo_corrente < self.__costo_ottimo or self.__costo_ottimo == -1:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        if costo_corrente >= self.__costo_ottimo != -1:
            return

        possibili_impianti = list(consumi_settimana.keys())

        for impianto_id in possibili_impianti:
            costo_spostamento = 0
            if ultimo_impianto is not None and impianto_id != ultimo_impianto:
                costo_spostamento = 5
            kwh_giorno = consumi_settimana[impianto_id][giorno -1]
            nuovo_costo= costo_corrente + kwh_giorno + costo_spostamento
            sequenza_parziale.append(impianto_id)
            self.__ricorsione(sequenza_parziale,giorno + 1, impianto_id, nuovo_costo, consumi_settimana)
            sequenza_parziale.pop()


    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        dati_settimana = {}

        for impianto in self._impianti:
            tutti_consumi= impianto.get_consumi()

            consumi_filtrati =[]
            for consumi in tutti_consumi:
                if  consumi.data.year == 2026 and consumi.data.month == mese and consumi.data.day <=7:
                    consumi_filtrati.append(consumi)

            consumi_filtrati.sort(key=lambda x: x.data)
            lista_KWh= []
            for consumi in consumi_filtrati:
                lista_KWh.append(consumi.kwh)
            dati_settimana[impianto.id] = lista_KWh

        return dati_settimana

