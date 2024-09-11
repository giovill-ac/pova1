# Room Organizer
Documentazione del progetto

Gruppo di lavoro:
- Giorgia Villano, 676577, g.villano@studenti.uniba.it
  
AA 2023-2024

## Introduzione

L'obiettivo di questo progetto è ottimizzare il posizionamento dei mobili in una stanza, rispettando vari vincoli e preferenze. Data una stanza con dimensioni specifiche, porte e mobili, la sfida consiste nel trovare la disposizione più efficiente dei mobili che soddisfi diverse condizioni, come vincoli di spazio, preferenze di vicinanza e posizionamento lungo le pareti. Questo problema di ottimizzazione viene affrontato utilizzando due diversi algoritmi: **Simulated Annealing** e **Stochastic Beam Search**.

## Sommario

Il codice utilizza due algoritmi di ottimizzazione per risolvere il problema del posizionamento dei mobili in una stanza. Gli algoritmi sono implementati in Python e utilizzano una rappresentazione della stanza e dei mobili in formato YAML. La stanza è definita dalle sue dimensioni, una lista di porte e una lista di mobili.

Ogni porta ha una posizione, una lunghezza e un'orientamento (orizzontale o verticale). Essa è definita tramite la seguente classe:

```python
class Door:
    def __init__(
        self, name: str, pos: Tuple[int, int], length: int, is_horizontal: bool
    ):
        self.name = name
        self.pos = pos
        self.length = length
        self.is_horizontal = is_horizontal
```


Ogni mobile è definito da un nome, dimensioni, colore, preferenze di posizionamento e, in alcuni casi, relazioni con altri mobili. Essi sono definiti tramite la seguente classe:

```python
class Furniture:
    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        color: str,
        preferred_on_wall: bool = False,
        nearby_furniture: list = [],
        front=Optional[FurnitureFront],
    ):
        self.name = name
        self.width = width
        self.height = height
        self.color = color
        self.preferred_on_wall = preferred_on_wall
        self.nearby_furniture = nearby_furniture
        self.front = front
```
```name``` e ```color``` non inficiano sull'algoritmo di ottimizzazione, ma sono utili per la visualizzazione della disposizione finale dei mobili. ```front``` è un attributo opzionale che indica se il mobile ha un fronte specifico, il suo valore può essere ```None```, ```"long_side"``` o ```"short_side"```. Dato che i mobili sono rettangoli possiamo specificare se il fronte del mobile è il lato lungo o il lato corto. ```nearby_furniture``` è una lista di mobili con cui si preferisce che il mobile corrente sia vicino.

Il sistema deve rispettare una serie di vincoli e preferenze, tra cui:

1. **Confini della Stanza**: I mobili devono rientrare nei confini della stanza, il che significa che la posizione e le dimensioni dei mobili non possono estendersi oltre la larghezza o l'altezza della stanza. Questo vincolo è automaticamente rispettato durante la generazione delle coordinate casuali dei mobili.
2. **Sovrapposizione dei Mobili**: I mobili non devono sovrapporsi tra loro e devono essere posizionati in modo che non si sovrappongano alle porte e al loro spazio di apertura.
3. **Posizionamento a muro**: Per alcuni mobili può essere specificato se preferiscono essere posizionati contro una parete. In tal caso il sistema cerca di posizionare il mobile in modo che il retro sia adiacente a una parete.
4. **Vicinanza**: Per alcuni mobili si preferisce che siano vicino ad altri mobili. Ad esempio, una sedia dovrebbe essere vicino a un tavolo. In tal caso il sistema cerca di posizionare i mobili in modo che siano vicini ai mobili specificati. Inoltre se un mobile ha un fronte specifico, il sistema cerca di posizionare il mobile in modo che il fronte sia rivolto verso il mobile specificato. Se entrambi i mobili hanno un fronte specifico, il sistema cerca di posizionare i mobili in modo che i fronti siano adiacenti.

La penalità per la violazione di ogni vincolo è specificata tramite una serie di variabili:

```python
OVERLAP_PENALTY = 100
WALL_PENALTY = 50
DOOR_PENALTY = 100
PENALTY_DISTANCE_MULTIPLIER = 10
NOT_FACE_TO_FACE_PENALTY = 100
```

Modificando questi valori è possibile regolare l'importanza dei vari vincoli e preferenze. Inoltre impostando una soglia di penalità è possibile definire quando una soluzione è accettabile.

La soluzione è rappresentata da una lista di mobili con le loro coordinate e orientazioni. Ad esempio:

```python
[
  (3, 4, "top"),
  (0, 0, "left"),
  (5, 5, "right"),
  ...
]
```

Dato che il problema è NP-hard, non è possibile trovare una soluzione ottimale in tempi ragionevoli. Per questo motivo vengono utilizzati due algoritmi di ottimizzazione: **Simulated Annealing** e **Stochastic Beam Search**.

**Argomenti di interesse**:
- Ricerca di soluzioni
- Ragionamento con vincoli e ottimizzazione


## 1. Ricerca di soluzioni

### Sommario

La ricerca di soluzioni è un'area dell'intelligenza artificiale che si occupa di trovare soluzioni a problemi complessi. Questi problemi possono essere di natura diversa, come la pianificazione, l'ottimizzazione o la previsione. La ricerca di soluzioni si basa su algoritmi euristiche che esplorano lo spazio delle soluzioni per trovare la migliore possibile. In questo progetto, la ricerca di soluzioni è utilizzata per trovare la disposizione ottimale dei mobili in una stanza, rispettando vari vincoli e preferenze.

### Strumenti utilizzati

Possiamo modellare il problema del posizionamento dei mobili in una stanza come una ricerca in un grafo, in cui i nodi rappresentano le diverse configurazioni dei mobili e gli archi rappresentano le possibili transizioni tra le configurazioni. La soluzione è rappresentata da una configurazione dei mobili che soddisfa i vincoli e le preferenze specificati.

### Decisioni di progetto

Le due decisioni di progetto principali riguardano la rappresentazione dello spazio di ricerca e come muoversi in esso.

1. **Rappresentazione dello Spazio di Ricerca**: Ogni possibile nodo è rappresentato da una lista finita di tuple, e ogni tupla rappresenta un mobile con le sue coordinate e orientamenti. Gli orientamenti sono "top", "bottom", "left" e "right", mentre le coordinate sono comprese tra 0 e la dimensione massima della stanza. Se si assume che il range sia discreto, il numero di possibili configurazioni è finito, ma comunque non trattabile in maniera esaustiva.
2. **Transizioni tra le Configurazioni**: Le transizioni tra le configurazioni sono rappresentate dalla modifica di un elemento nella lista. Quindi si racchiudono un due operazioni: **spostamento di un mobile** e **rotazione di un mobile**. La scelta tra le due possibili operazioni è casuale, ma se un mobile e quadrato e non ha un fronte specifico, verrà scelto lo spostamento.

## 2. Ragionamento con vincoli e ottimizzazione

### Sommario

Il ragionamento con vincoli è una branca dell'intelligenza artificiale che si concentra sulla risoluzione di problemi complessi attraverso l'uso di vincoli e relazioni tra variabili. In questo progetto, viene impiegato per assicurare che la disposizione dei mobili in una stanza rispetti vari vincoli e preferenze, come il mantenimento entro i confini della stanza, il posizionamento dei mobili in prossimità di altri elementi d'arredo e l'aderenza di alcuni mobili alle pareti.

### Strumenti utilizzati

Per risolvere il problema del posizionamento dei mobili in una stanza, vengono utilizzati due algoritmi di ottimizzazione: **Simulated Annealing** e **Stochastic Beam Search**. Entrambi gli algoritmi sono euristici e cercano di trovare la disposizione ottimale dei mobili rispettando i vincoli e le preferenze specificati.

#### 1. **Simulated Annealing**

Il **Simulated Annealing** è un algoritmo di ottimizzazione ispirato al processo di ricottura in metallurgia. L'algoritmo cerca di minimizzare una funzione di costo regolando iterativamente la configurazione (in questo caso, il posizionamento dei mobili), accettando occasionalmente soluzioni peggiori per sfuggire ai minimi locali. Il processo inizia con una "temperatura" alta che consente un'esplorazione maggiore e, gradualmente, la temperatura si riduce man mano che l'algoritmo converge verso una soluzione ottimale.

#### 2. **Stochastic Beam Search**

La **Stochastic Beam Search** è un algoritmo euristico di ricerca locale che esplora lo spazio delle soluzioni mantenendo solo un numero limitato di soluzioni promettenti. A differenza della ricerca in ampiezza tradizionale, che esplora tutte le possibili configurazioni, il Beam Search limita la ricerca mantenendo solo un numero fisso di configurazioni migliori, noto come larghezza del raggio ("beam width"). Questo approccio consente di bilanciare l'esplorazione e l'efficienza, evitando di esplorare tutte le configurazioni ma cercando comunque soluzioni promettenti.

### Configurazione di Esempio della Stanza (Formato YAML)

```yaml
room_width: 10
room_height: 10

doors:
  - name: Porta d'ingresso
    position: [5, 0]
    length: 2
    is_horizontal: true
  - name: Porta del balcone
    position: [0, 6]
    length: 2
    is_horizontal: false

furnitures:
  - name: Divano
    width: 4
    height: 3
    color: red
    front: long_side
  - name: Sedia
    width: 1
    height: 1
    color: white
    preferred_on_wall: false
    nearby_furniture: [Tavolo]
  - name: Tavolo
    width: 2
    height: 2
    color: brown
    preferred_on_wall: false
  - name: TV
    width: 2
    height: 1
    color: grey
    preferred_on_wall: true
    front: long_side
    nearby_furniture: [Divano]
  - name: Libreria
    width: 3
    height: 1
    color: violet
    front: long_side
    preferred_on_wall: true
  - name: Scrivania
    width: 4
    height: 2
    color: 'orange'
    front: long_side
    preferred_on_wall: true
  - name: Sedia da ufficio
    width: 1
    height: 1
    color: 'blue'
    preferred_on_wall: false
    nearby_furniture: [Scrivania]
```

### Disposizione della Stanza
- Dimensioni della Stanza: La stanza è una griglia 10x10 in cui vengono posizionati i mobili e le porte.
- Porte: La stanza ha due porte:
  - Una porta d'ingresso, che è lunga 2 unità ed è posizionata orizzontalmente nella parte inferiore della stanza.
  - Una porta del balcone, anch'essa lunga 2 unità, ma posizionata verticalmente sul lato sinistro della stanza.
- Mobili: La stanza contiene vari elementi di arredo, ognuno con dimensioni specifiche, colore e preferenze di posizionamento. Ad esempio:
  - Il Divano ha dimensioni 4x3, è rosso e preferisce essere posizionato contro una parete.
  - La Sedia è 1x1, bianca, e deve essere posizionata vicino al Tavolo.
  - Il TV dovrebbe idealmente essere posizionato vicino al Divano.
- Vincoli e Preferenze
  1. Confini della Stanza
    I mobili devono rientrare nei confini della stanza, il che significa che la posizione e le dimensioni dei mobili non possono estendersi oltre la larghezza o l'altezza della stanza.

  2. Posizionamento dei Mobili
    Ogni mobile ha una larghezza e un'altezza specifiche che devono essere rispettate. Alcuni mobili hanno preferenze per essere posizionati contro la parete (es. Divano, TV, Libreria) per ottimizzare l'uso dello spazio e migliorare l'estetica della stanza.

  3. Accesso alle Porte
    Le porte non devono essere bloccate dai mobili. Sia la porta d'ingresso che quella del balcone devono rimanere accessibili, il che significa che nessun mobile deve sovrapporsi alle porte.

  4. Preferenze di Vicinanza
    Alcuni mobili hanno preferenze per essere posizionati vicino ad altri elementi. Ad esempio:

    - La Sedia deve essere posizionata vicino al Tavolo per creare un'area di seduta coesa.
    - Il TV deve essere posizionato vicino al Divano per formare una zona di intrattenimento.
  5. Preferenze di Posizionamento a Parete
    Alcuni mobili, come il Divano, la Libreria e il TV, preferiscono essere posizionati contro una parete per massimizzare lo spazio a disposizione e migliorare la funzionalità della stanza.

### Decisioni di progetto

Per ogni algoritmo di ottimizzazione, sono state scelti e testati diversi parametri per trovare la configurazione ottimale della stanza.

#### 1. Simulated Annealing

Per l'algoritmo di Simulated Annealing, sono stati scelti i seguenti parametri:

- **Temperatura Iniziale**: La temperatura iniziale determina quanto l'algoritmo accetta soluzioni peggiori all'inizio del processo. Una temperatura più alta consente una maggiore esplorazione dello spazio delle soluzioni.
- **Temperatura Finale**: La temperatura finale indica quando l'algoritmo dovrebbe convergere verso una soluzione ottimale. Una temperatura più bassa consente una maggiore precisione nella ricerca della soluzione ottimale.
- **Numero di steps**: Il numero di steps determina quanti passaggi dell'algoritmo vengono eseguiti in totale. Un numero maggiore di steps consente una maggiore esplorazione dello spazio delle soluzioni, ma richiede più tempo di calcolo.

La temperatura diminuisce velocemente all'inizio e rallenta man mano che ci si avvicina alla fine, seguendo una curva esponenziale decrescente.

#### 2. Stochastic Beam Search

Per l'algoritmo di Stochastic Beam Search, sono stati scelti i seguenti parametri:

- **Larghezza del Raggio**: La larghezza del raggio determina quanti nodi vengono mantenuti in ogni iterazione dell'algoritmo. Una larghezza del raggio maggiore consente una maggiore esplorazione dello spazio delle soluzioni, ma richiede più memoria e tempo di calcolo.
- **Numero di Generazioni**: Il numero di generazioni indica quante iterazioni dell'algoritmo vengono eseguite. Un numero maggiore di generazioni consente una maggiore esplorazione dello spazio delle soluzioni, ma richiede più tempo di calcolo.
- **Temperatura Iniziale**: La temperatura determina la probabilità di accettare una soluzione peggiorativa. Una temperatura più alta consente una maggiore esplorazione dello spazio delle soluzioni.

### Valutazione

La valuatazione dell'algoritmo è stata effettuata in basse alla loro capacità di trovare una soluzione e il tempo impiegato per farlo. Di conseguenza, minore è il valore della funzione di costo, migliore è la soluzione. Inoltre, il tempo di esecuzione è un parametro importante per valutare le prestazioni dell'algoritmo.

Considerando l'esempio suddetto, abbiamo settato i seguenti parametri per il Simulated Annealing:

<!-- Tabella -->
| Parametro | Valore |
|-----------|--------|
| Temperatura Iniziale | 5000 |
| Temperatura Finale | 1.0 |
| Numero di Steps | 50000 |

Con tale configurazione, l'algoritmo di Simulated Annealing è in grado di trovare una soluzione con costo 0 in circa 5 secondi (considerando l'hardware attuale). Tuttavia, abbiamo notato eseguendo più volte l'algoritmo che potrebbe trovare anche soluzioni con costo maggiore. In visione di un lavoro futuro, sarebbe interessante stimare la probabilità di trovare una soluzione rispetto al numero di steps.

Per quanto riguarda il Stochastic Beam Search, abbiamo settato i seguenti parametri:

<!-- Tabella -->

| Parametro | Valore |
|-----------|--------|
| Larghezza del Raggio | 100 |
| Numero di Generazioni | 20 |

Con tale configurazione l'algoritmo di Stochastic Beam Search è in grado di trovare una soluzione con costo 0 in circa 8-10 secondi (considerando l'hardware attuale).

Potremmo valutare la complessità degli algoritmi anche rispetto al numero di valutazioni della funzione di costo. Nel caso del simulated annealing, il numero di valutazioni della funzione di costo è proporzionale al numero di steps, mentre nel caso del beam search è proporzionale al prodotto tra il numero di generazioni e la larghezza del raggio. Quindi, in tal caso sarebbe più efficiente l'algoritmo della stochastic beam search. Inoltre, essa consente anche un certo grado di parallelismo, in quanto è possibile esplorare più soluzioni contemporaneamente.

Esempio di soluzione trovata dagli algoritmi:

![Soluzione Beam Search](images/final_furniture_placement_room1.png)

Consideriamo adesso una stanza più complessa:

```yaml
room_width: 15
room_height: 12

doors:
  - name: Ingresso principale
    position: [7, 0]
    length: 3
    is_horizontal: true
  - name: Porta della cucina
    position: [15, 5]
    length: 2
    is_horizontal: false
  - name: Porta del balcone
    position: [0, 9]
    length: 2
    is_horizontal: false

furnitures:
  - name: Divano
    width: 5
    height: 2
    color: 'red'
    front: long_side
    preferred_on_wall: true
    nearby_furniture: [Tavolino da caffè]
  - name: Tavolino da caffè
    width: 2
    height: 2
    color: 'brown'
    preferred_on_wall: false
  - name: Mobile TV
    width: 4
    height: 1
    color: 'brown'
    front: long_side
    preferred_on_wall: true
    nearby_furniture: [Divano]
  - name: Tavolo da pranzo
    width: 3
    height: 3
    color: 'darkgreen'
    preferred_on_wall: false
  - name: Sedia da pranzo 1
    width: 1
    height: 1
    color: 'white'
    preferred_on_wall: false
    nearby_furniture: [Tavolo da pranzo]
  - name: Sedia da pranzo 2
    width: 1
    height: 1
    color: 'white'
    preferred_on_wall: false
    nearby_furniture: [Tavolo da pranzo]
  - name: Sedia da pranzo 3
    width: 1
    height: 1
    color: 'white'
    preferred_on_wall: false
    nearby_furniture: [Tavolo da pranzo]
  - name: Sedia da pranzo 4
    width: 1
    height: 1
    color: 'white'
    preferred_on_wall: false
    nearby_furniture: [Tavolo da pranzo]
  - name: Libreria
    width: 3
    height: 2
    color: 'darkviolet'
    front: long_side
    preferred_on_wall: true
  - name: Letto
    width: 6
    height: 4
    color: 'lightyellow'
    preferred_on_wall: false
  - name: Comodino 1
    width: 1
    height: 1
    color: 'lightgrey'
    preferred_on_wall: false
    nearby_furniture: [Letto]
  - name: Comodino 2
    width: 1
    height: 1
    color: 'lightgrey'
    preferred_on_wall: false
    nearby_furniture: [Letto]
  - name: Armadio
    width: 4
    height: 2
    color: 'navy'
    front: long_side
    preferred_on_wall: true
  - name: Scrivania
    width: 4
    height: 2
    color: 'orange'
    front: long_side
    preferred_on_wall: true
  - name: Sedia da ufficio
    width: 1
    height: 1
    color: 'blue'
    preferred_on_wall: false
    nearby_furniture: [Scrivania]
```

Utlizzando gli stessi parametri della stanza precedente, l'algoritmo di Simulated Annealing è in grado di trovare una soluzione con costo 100 in circa 20 secondi.

Anche aumentando il numero di steps a 1000000, l'algoritmo non è in grado di trovare una soluzione con costo 0.

Utilizzando gli stessi parametri della stanza precedente, l'algoritmo di Stochastic Beam Search è in grado di trovare una soluzione con costo 400 in circa 1 minuto.

Aumentando il numero di generazioni a 100 e la larghezza del raggio a 150, l'algoritmo è in grado di trovare una soluzione con costo 90 in circa 10 minuti.

Soluzione trovata dalla Stochastic Beam Search:

![Soluzione Beam Search](images/final_furniture_placement_room2.png)

# Conclusione

Il progetto Room Organizer ha affrontato con successo il complesso problema di ottimizzare il posizionamento dei mobili in una stanza, rispettando una serie di vincoli e preferenze. Attraverso l'implementazione di due algoritmi di ottimizzazione, Simulated Annealing e Stochastic Beam Search, si è dimostrato che è possibile trovare soluzioni efficaci per configurazioni di stanze di diversa complessità.

## Risultati chiave

1. **Efficacia degli algoritmi**: Entrambi gli algoritmi si sono dimostrati capaci di trovare soluzioni valide, con il Simulated Annealing che ha mostrato prestazioni particolarmente buone per stanze di complessità media, trovando soluzioni ottimali in tempi brevi.

2. **Scalabilità**: Con l'aumento della complessità della stanza (più mobili e vincoli), il Stochastic Beam Search ha dimostrato una maggiore robustezza, riuscendo a trovare soluzioni accettabili anche per configurazioni più complesse, sebbene richiedesse più tempo.

3. **Flessibilità del modello**: Il sistema sviluppato si è dimostrato flessibile, capace di gestire diverse configurazioni di stanze, mobili e vincoli, rendendolo adattabile a vari scenari d'uso.

4. **Trade-off tempo-qualità**: Si è osservato un chiaro trade-off tra il tempo di esecuzione e la qualità delle soluzioni trovate, specialmente per configurazioni più complesse. Aumentando il numero di iterazioni o la larghezza del raggio, è stato possibile ottenere soluzioni migliori a scapito di un maggior tempo di calcolo.

## Limitazioni e sviluppi futuri

1. **Ottimizzazione dei parametri**: Un'area di miglioramento potrebbe essere l'implementazione di un sistema per ottimizzare automaticamente i parametri degli algoritmi in base alla complessità del problema.

2. **Parallelizzazione**: Data la natura del Stochastic Beam Search, un'implementazione parallela potrebbe portare a significativi miglioramenti delle prestazioni.

3. **Interfaccia utente**: Lo sviluppo di un'interfaccia grafica user-friendly potrebbe rendere il sistema più accessibile a utenti non tecnici.

4. **Vincoli avanzati**: L'introduzione di vincoli più sofisticati, come considerazioni estetiche o funzionali più complesse, potrebbe aumentare l'utilità pratica del sistema.

5. **Analisi statistica**: Una valutazione statistica più approfondita delle prestazioni degli algoritmi potrebbe fornire insights preziosi sulla loro affidabilità e efficacia in diversi scenari.

In conclusione, il progetto Room Organizer ha dimostrato la validità dell'approccio basato su algoritmi di ottimizzazione per risolvere problemi di disposizione spaziale. I risultati ottenuti forniscono una solida base per ulteriori sviluppi e raffinamenti, aprendo la strada a potenziali applicazioni pratiche nel campo del design d'interni e della pianificazione degli spazi.