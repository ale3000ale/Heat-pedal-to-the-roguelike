// Pilota scelto nell'elenco dei negozi (voce "Negozio" della barra).
// La pagina del negozio lo legge una volta all'apertura e lo azzera, così entrando
// dalla pagina del campionato si parte sempre dal primo pilota.
class ShopSelection {
	pilotId = $state<number | null>(null);
}

export const shopSelection = new ShopSelection();
