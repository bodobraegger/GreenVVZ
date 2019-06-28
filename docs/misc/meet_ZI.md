# Mail planning:
## inital
 Zugriff auf den jetzigen Server kriegt. Der Code ist aber soweit ich sehe komplett
'Magic Numbers'  hardcoded
Auf jeden Fall sollte die UZH angefragt werden, ob man den Server auf einem UZH server und Domain hosten kann, anstelle eines privaten Servers. 
Anstatt langen Wartezeiten pollen
## summary
Polling Server Struktur einrichten, Steueradministration für Wartung zugänglich machen
Keyword-Search neu/smart implementieren (jetzt gerade ist es einfach für jeden Searchterm, ein mal alles durchsuchen, am Ende Duplikate löschen)
Exemplarische 'Code-Smells' identifizieren, dokumentieren und beseitigen (grundlegende Code Verbesserungen), sowie dokumentieren und zeigen, wieso dies Code-Smells sind.
Eine Bessere Datenstruktur für die Module in der Datenbank finden, so dass man  effizient nach Semester und Studiengang filtern kann.
User Interface revamp, um neue Funktionalität (Suche nach Studiengang & Semester im Stil des Uni-Designs)
## their summary
Änderungen im Backend (Frequenz des Abgleichs mit dem VVZ, Vermeidung von Harcoding, grundlegende Code Verbesserungen….)
Verbesserung der Datenstruktur inkl. Filterfunktionalität (hierbei kann man auch über das Interface nachdenken, inkl. Filtern nach Studiengang)
Verbesserung der Keyword-Search (nochmal gemeinsam schauen, wieviel davon noch möglich sein wird)
## initial work summary
16 h: Lokaler setup
benötigte Packages ausfindig machen & updaten, 
Testen (ist der bereitgestellte Code komplett? Funktioniert alles so wies sollte? Ggf. Code überarbeiten)
24 h: Setup auf UZH Server
Provision des Backend-Servers samt den benötigten Packages
erneutes Testen (Ggf. Code überarbeiten)
schriftliche Dokumentation des Setup-Prozesses (unter Berücksichtigung der bestehenden Dokumentation / Bachelorarbeit soweit möglich)
16 h: Einarbeit ins UZH CMS
Frontend Komponenten ins CMS einbetten und testen (ggf. Code überarbeiten)
schriftliche Dokumentation dieses Teil des Setups
(Hier kann ich mir auch gut Gedanken machen, ob der jetzige Setup vereinfacht werden könnte für weitere Organisationseinheiten, so dass diese das Tool auch brauchen könnten - und was dazu nötig wäre.)
8 h: Einführung in die Wartung und Administration vom neuen Nachhaltigkeits-VVZ Setup
ggf. schriftliche Dokumentation weiter anpassen.

# Meet Jan
·     Beseitigung der Ladezeit bei der Admin-Ansicht
    o     Einbettung einer iFrame-Page, die direkt vom greenvvz Server bereitgestellt wird
·     Jahr und Semester anzeigen. 
·     Frontend-Filter-Funktionalität: Jetzt hat man die Möglichkeit, die bestehenden Daten von diesem und dem letzten Jahr nach Semester zu filtern. Dies kann ich jetzt einfach auf weitere Datenpunkte anpassen, so dass man dann ggf. nach Studiengang filtern kann. 
·     Für Suchbegriffe-Vorschläge: Alle Vorschläge anzeigen, auch solche, die schon gespeichert sind. Diese entsprechend markieren, z.b. mit deaktivierten 'Anzeigen‘ Knopf 
 

·     Vorschläge ordnen nach Semester, oder angezeigt/verborgen/ignoriert. —> war das in der admin oder in der public Ansicht? Kannst dus nochmal etwas genauer beschrieben, verstehe es grad net.
    --> das wäre in der admin ansicht, s.d. man schnell eine Übersicht über alle ‘neuen’ Vorschläge bekommen kann  —> Heisst neu, Vorschläge aus dem neuen Semester oder aufgrund eines Suchbegriffs. Man sollte am Ende genau wissen, was bei einem Semesterwechsel passiert (werden die alten einfach gelöscht, kriege ich als User davon was mit, wie werden die aus dem neuen aufgenommen). Darüber hinaus wäre es gut, wenn man bei jedem Modul/LV sieht, durch welchen Suchbegriff wurde sie gefunden, ist sie verborgen oder nicht? Nach Semester und Suchbegriff sollte man vermutlich auch sortieren können.

·     Input validation, so dass keine unzulässigen / unbrauchbaren Suchbegriffe benützt werden können —> gerne machen, Dokumentiere bitte auch was du validierst und senden mir nochmal zur Sicherheit kurz zu, dass ich drüber schauen kann
--> also, im grunde wäre das: modulnummer - nur zahlen erlauben, suchbegriffe - nur wörter, die nicht mit leerschlag beginnen, mehrfache leerschläge unterbinden —> ok
 

·     Backend-Datenstruktur ändern, um nicht nur Module, sondern v.a. Lerhveranstaltungen zu speichern, und zu diesen jeweils zu welchen Modulen sie gehören, und dazu wiederum welche Module zu welchen Studienprogrammen gehören, bis zu ggf. Studiengängen. —> Das wäre perfekt, man müsste sich dann generell mit dem ASP für VVZ zur Struktur des VVZ abstimmen. Thomas Schwan ist hier der Ansprechpartner. Ich habe gerade schonmal mit ihm telefoniert und er ist bereit sich mit uns zusammenzusetzen. Könntest Du mal 2-3 Termin Vorschlagen die dir passen würden, dann kann ich diese prüfen und wir können ihm diese vorschlagen. Ich wäre beim ersten Meeting wo es noch um Fragen geht ob wir Lehrveranstaltungen oder Module anzeigen gerne dabei. 
--> Nächste Woche würde würde für mich der Dienstag, 23. gehen, oder auch sonst nächste Woche, aber wahrscheinlich nur per Skype.
Übernächste Woche wäre der Montag, 29.04, vor 12:00, nach 14:00; oder Donnerstag, 02.05, nach 14:00; oder Freitag, 03.05 nach 13:00 gut.
—> ok. Ich nehme mal 29.04 vor 12 Uhr oder nach 14 Uhr und 02.05. nach 14 Uhr.

# Meet ZI

Eine grundlegende Frage ist, ob es eine Dokumentation gibt über die OData Schnittstelle des VVZ der UZH, worin die verschiedenen öffentlichen Endpunkte aufgelistet sind. Das wäre nützlich, um mir die folgenden Fragen selber beantworten zu können.
Im Moment sieht es so aus, als ob man...
ein anfängliches Request machen muss, um eine Liste von Lehrveranstaltungen zu bekommen, und dann jeweils 
per Lehrveranstaltung ein Request für die volle LV-Detailseite (Obschon nur der Teil, in welchen Modulen die LV vorkommt, relevant ist), dann jeweils 
ein Request pro Modul-Detailseite, in dem das LV vorkommt, um die zugehörigen Studienprogramme zu finden
und pro M-Detailseite ein Request für die SP-Detailseite, um da den übergeordneten Studiengang zu finden, falls das relevant sein sollte.
Das Problem dabei ist, dass das doch relativ viel Requests / Daten sind pro Suchanfrage. 
Die Frage dabei wäre, ob man die Requests besser zuschneiden kann, um nur die relevanten Infos zu bekommen, nicht die gesamten Detailseiten.
Eine weitere Frage wäre dann, ob Herr Schwan uns raten würde, diese Requests jeweils pro Suchanfrage zu machen (die Daten gar nicht in einer eigenen Datenbank zu speichern), oder die Daten zu speichern und selber zu trimmen - also quasi über Nacht updaten, und dann mit den täglichen Infos schneller arbeiten zu können. Ich bin mir nicht sicher, ob die Performanz so viel besser wäre.
Die letzte Frage ist, ob man die Architektur / das gewählte Framework grundlegend zu einem Webserver ändern sollte / muss, der asynchrone Requests besser unterstützt als das Flask Framework, um die Performanz hoch zu halten. Ich hoffe, dass das nicht der Fall sein wird, und ich die requests an das VVZ doch asynchron durchführen kann. Das kann mir Herr Schwan auch nicht beantworten, aber ich werde es im Verlaufe der Implementation sehen.

1) Kurzvorstellung „GreenVVZ“
2) Gibt es eine Doku zur API vom VVZ?
    yes
3) Sollen wir lieber Module oder Lehrveranstaltungen anzeigen? Wo stehen normalerweise die wichtigen Informationen?
   modul > LV, aber nonig einig
   regel: modul besser gepflegt
   relevante info einheit
   uni-philosophie: go for modul
4) Gibt es im System einen Zeiger LV à Modul à Studienprogramm à Studiengang?
    nein
5) Wann werden Änderungen am Inhalt der Kurse, Module, etc. gemacht? Was passiert bei Änderungen?
   gibt planung: 
   für HS im Juli
   für FS im November
   er schickt uns 😺
   aber laufende änderungen, im prinzip sicht auf SAP DB
   einmal stündlich
6) Wie lange in die Vergangenheit werden die Semester angezeigt?
   die letzten 10
7) Wird es in nächster Zeit relevante Änderungen am VVZ geben?
   kleinere anpassungen, im november änderung: sprachfilter auf ebene modul (neue flag) und LV (nur filter) 
8) Macht eine Suche nach Studiengang und Studienprogramm Sinn oder nur nach einem von beiden?
   nur studienprogramm
9)  Macht es Sinn die Requests pro Suchanfrage zu machen oder in eine DB zwischenzuspreichern?
    DB!
10) Architektur synchron/asynchron (Performance)?
    rate limiting?

# Feedback skype:
- [x] public: -Lehrveranstaltungen +Modul
- [x] beruht auf stichwortsuche (machen sie)
- [x] link target _blank
- [x] filter löschen button
- [x] filter genügend platz: 1227px?
- [x] methoden zeigt keine module?
- [x] green vvz ohne public (machen sie)
- [x] filtern statt auswählen
- [x] vorschläge von welchem vorschlag?
- [x] anzahl 
- [x] ladeindiciator