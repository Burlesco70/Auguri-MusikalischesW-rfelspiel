# Auguri con Musikalisches Würfelspiel

Basato sull'implementazione (https://github.com/Xpktro/wurfelspiel di Moisés Cachay Tello, Apache License, Version 2.0) del Musikalisches Würfelspiel (K516f), gioco compositivo attribuito (con qualche dubbio) a W.A. Mozart.

Lo script, originariamente realizzato per la pubblicazione periodica su twitter, prevede la generazione dello spartito, dell'audio e alla fine di un file video.
Si basa da un file master template in formato lilypond (`score.ly`) che contiene tutte le battute del gioco K516f. Lo script `auguri_wurfelspiel.py` fa parsing del template e implementa le regole per generare una nuova variazione delle 16 battute ad ogni esecuzione, simulando il lancio di due dati per ogni battuta.
Con il file spartito in formato lilypond, viene generato lo spartito in formato PNG e un file musicale in formato MIDI. Utilizzando TiMidity++ e un gradevole file soundfont 1729 Harpsichord viene generato il WAV che, alla fine, è renderizzato con FFmpeg, insieme all'immagine, nel video finale.

Le modifiche permettono di personalizzare il video generato con dedica, titolo e mittente degli auguri.

# Requirements
* Python 3
* [Lilypond](http://lilypond.org/)
* [TiMidity++](http://timidity.sourceforge.net/)
* [FFmpeg](https://www.ffmpeg.org/)
* [Soni Musicae Blanchet 1729 Soundfount](http://sonimusicae.free.fr/blanchet1-en.html)

# Installazione

* Clona questa repo.
* Scarica le applicazioni come da requirements
* Scarica il file soundfont e 
* Installa le dipendenze usando il poetry file `pyproject.toml`
```
poetry install
```
* Configura TiMidity++ tramite il file di configurazione `timidity.cfg` seguendo le istruzioni del tool. 
Il modo più semplice è quello di specificare il file soundfond, ad esempio
```
soundfont F:\Programmi\TiMidity++-2.15.0\Blanchet-1720.SF2
```

# Utilizzo
Crea il file di ambiente .env dove valorizzare il PATH agli eseguibili, prendendo come esempio `.env.example`


Le modifiche permettono di personalizzare il video generato con:
- dedica: unico parametro (opzionale) dello script
- titolo: specificabile personalizzando la variabile `title` nel main
- mittente: specificabile personalizzando la variabile `greetings_from` nel main
```
python auguri_wurfelspiel.py Mario
```


# License
Copyright 2022-2023 Moisés Cachay Tello e Mario Nardi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
