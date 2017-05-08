Detalii si explicatii implementare:

Stage 1:

Am incercat sa abstractizez codul cat am putut, sa "ascund" tehnologiile din spate, mai
ales la baza de date.

Din cele 3 componente ale aplicatiei, am inceput cu baza de date.
Prima idee a fost sa am 2 colectii, una pentru submisii si una pentru comments.
Apoi am realizat ca in use case-ul aplicatiei nu prea este mare diferenta intre
modul de comportare al submisiilor si al comentariilor, asa ca se poate profita
de faptul ca Mongo este schema-free si am unit cele 2 colectii intr-una singura.
Aceasta ar fi cuprins absolut tot, ordonat intai dupa subreddit si apoi dupa timestamp.

Dupa inca putin timp am realizat, totusi, ca nu se pot face request-uri pe mai mult
de un subreddit, asa ca o arhitectura cu o colectie per subreddit ar fi mai buna,
deoarece nu ar incarca o colectie foarte mult si nici nu ar mai fi nevoie de o
sortare/un index dupa subreddit.
Aceasta este, deci, varianta finala pentru care am optat.

database.py contine doar o clasa ce este un wrapper peste operatiile CRUD ale
bazei de date, pentru a fi mai usoara rescrierea codului in caz ca tehnologia
se schimba.

A doua componenta a aplicatiei este scriptul ce apeleaza API-ul reddit.
Acesta isi citeste configuratia dintr-un fisier, isi initializeaza conexiunea
la db si porneste un loop infinit. Aici, trimite un request la reddit
(prin praw) o data la X secunde, fetch-uind cele mai noi submisii si comments.
Clasa retine in memorie un dict cu data pana la care au fost inserate date
noi in db, astfel avand un control mai mare si nefiind nevoie de upsert
in loc de insert.
O problema aici este faptul ca, desi pentru submisii exista acest lucru,
comments nu se pot fetch-ui incepand de la un anumit timestamp (sau cel putin
nu am descoperit eu cum), astfel ca am fost fortat sa iau cele mai noi Y comentarii.
Ramane responsabilitatea user-ului sa stabileasca X si Y astfel incat sa fie sigur ca
in ultimele X secunde au fost postate maxim Y comentarii.

O imbunatatire a timpului de rulare am adus-o prin spawn-area unor worker threads,
ce fetch-uiesc date pentru subreddit-urile cu numerele de forma
(k * numar_threads) + thread_curent.
Numarul de thread-uri este definit in config file, iar in cazul in care acesta
este 1, thread-ul master executa direct polling-ul.

O alta problema de care m-am lovit ar fi ca nu am gasit un mod (relativ simplu)
de a opri scriptul gracefully. Stiu ca in challenge scrie ca nu trebuie sa fie
fault-tolerant, insa mi se pare urat, mai ales intr-un mediu threaded, sa fie
oprit brutal.
M-am gandit sa fac un signal handler pentru SIGINT, insa acesta ajunge doar la
master thread, deci ar fi trebuit creat un canal de comunicatie catre workeri,
asa ca am renuntat la idee.

Astfel, thread-urile nu se termina niciodata, deci nu se ajunge la join :) .

Ultima componenta a aplicatiei este serverul web.
Aceasta este cea mai simpla componenta. Am folosit Flask, iar serverul stie
doar sa raspunda la request-uri de pe ruta /items/. Daca unul din parametri
lipseste sau este accesata alta ruta, el raspunde cu 404.
Pentru a returna datele necesare, el face doar un query la baza de date interna.
Serverul este si el threaded, deci poate servi mai multe request-uri.



Stage 2:
Pentru a suporta parametrul 'keyword', am adaugat un text index compus pe campurile
title si text.
Pentru stage 1 am adaugat un index pe campul timestamp.
Am verificat ca ambii indecsi functioneaza corect analizand planul returnat de
explain() pe cursorul returnat de query.
Rezultatele sunt sortate descrescator.



Stage 3:
Pentru suita de teste am folosit unittest si mock. Consider ca sunt suficiente teste pentru
baza de date si server, poate doar scriptul ar fi putut avea mai multe teste,
insa este mai dificil cu wait time-ul, instanta de praw si thread-urile.
Am structurat fisierele cu teste astfel incat sa poata fi rulate cu runnerul nose.



Stage 4:
Am creat cate un Dockerfile pentru fiecare proces.
Cel pentru db extinde imaginea oficiala de mongodb, iar celelalte extind imaginea de
Python 2.7. Fiecare are in *_requirements.txt pachetele de pip necesare.
In plus, exista si un fisier docker-compose.yml care leaga cele 3 containere.


Am incercat sa scriu codul fara un linter, ca sa vad daca-mi pot mentine un stil constant
pe toata aplicatia. Am folosit:
- single quotes in loc de double (obisnuinta din JS)
- camel case in loc de snake case (acolo unde s-a putut, unittest sau nose obliga totusi la
snake case)
- import in loc de from X import Y - pare mai clean sa nu fie poluat namespace-ul
- tabs in loc de spatii, mai putin in .yml care vrea neaparat spatii
- imports si dict keys in ordine alfabetica

A fost un challenge interesant, din care am invatat chestii cool. Cred ca cea mai dificila
parte a fost stage 4, unde mi-am batut capul ceva timp cu hostname-uri si porturi. Sunt sigur
ca se pot aduce imbunatatiri multe aplicatiei, atat din punct de vedere al arhitecturii cat si al performantei.
