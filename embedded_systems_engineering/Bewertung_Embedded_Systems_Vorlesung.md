# Bewertung der Embedded Systems Vorlesungsreihe (Decks 0–6)

**Kriterien:** Fluss · Plausibilität · Niveau (HAW)
**Bewertungsmaßstab:** HAW Bachelor/Master – anwendungsorientiert, industrienah, methodisch fundiert

---

## Schnellübersicht

| Deck | Thema | Fluss | Plausibilität | Niveau |
|------|-------|-------|---------------|--------|
| 0 | Intro Embedded Systems | ★★★★☆ | ★★★★★ | ★★★★★ |
| 1 | Software Engineering | ★★★★☆ | ★★★★★ | ★★★★☆ |
| 2 | Modellierung (UML) | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| 3 | Endliche Automaten & Statecharts | ★★★★★ | ★★★★★ | ★★★★☆ |
| 4 | Timed Automata | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| 5 | Verifikation mit UPPAAL | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| 6 | C + Rust | ★★★☆☆ | ★★★★★ | ★★★★★ |

---

## 1. Fluss – Didaktische Kohärenz und narrative Struktur

### Gesamtbild

Die Reihe hat einen erkennbaren roten Faden: vom informativen Überblick (0–1) über konzeptuelle Modellierung (2–3) zur formalen Verifikation (4–5) und schließlich zur Implementierungsebene (6). Die Kernsequenz Decks 3–5 ist die stärkste Einheit der Reihe – sie baut aufeinander auf wie ein Lehrbuchkapitel.

### Deck 0 – Einführung

Der Einstieg gelingt mit konkreten, greifbaren Alltagsbeispielen (ABS, Herzschrittmacher, Flugzeugsteuerung, IoT). Die Relevanz ist sofort spürbar. Gut: Die schrittweise Erarbeitung der Begriffsdefinition vermeidet einen trockenen „Definition zuerst"-Einstieg.

**Kritik:** Mit 55+ Folien ist Deck 0 deutlich zu lang für eine Einführungsveranstaltung. Der Detailgrad an manchen Stellen (z. B. Architekturdiagramme) sollte in spätere, thematisch passendere Decks verlagert werden. Außerdem fehlt eine grafische **Kursroadmap** – ein Überblicksschaubild, das alle Decks und ihre inhaltlichen Verbindungen zeigt, würde Studierenden von Beginn an Orientierung geben.

### Deck 1 – Software Engineering

Der Fluss von allgemeinen SE-Prinzipien hin zu ES-spezifischen Praktiken (V-Modell → AUTOSAR) ist logisch und gut motiviert. Die Brücke zur Industrie wird früh gezogen, was für eine HAW wichtig ist.

**Kritik:** Übergänge zwischen den Themenblöcken (z. B. Requirements Engineering → Teststrategien → AUTOSAR) sind inhaltlich korrekt, aber ohne explizite Lernzielformulierungen oder Überleitungssätze etwas abrupt. Einzelne Folien wirken wie isolierte Listen – mehr Kontext würde helfen.

### Deck 2 – Modellierung (UML)

Das Deck erfüllt eine wichtige Brückenfunktion zwischen SE (Deck 1) und formaler Modellierung (Deck 3). Die Auswahl der UML-Typen – insbesondere Timing-Diagramme und Statecharts – ist zielführend und auf ES ausgerichtet.

**Kritik:** Es fehlen explizite Vorausgriffe auf Deck 3. Aussagen wie „Die State Machines, die wir hier kennenlernen, werden wir in Deck 3 formalisieren" würden den Übergang nahtloser machen. Auch SysML als Alternative zu UML für Systems Engineering könnte kurz erwähnt werden, um das Bild der Modellierungswelt zu vervollständigen.

### Deck 3 – Endliche Automaten & Statecharts

Der didaktische Aufbau von einfachen FSMs (Mealy/Moore) über hierarchische Statecharts zu orthogonalen Regionen ist mustergültig. Der Schwierigkeitsgrad steigt graduell; jede Erweiterung ist durch ein konkretes Motivationsbeispiel eingebettet. **Bestes Deck der Reihe im Hinblick auf den inneren Fluss.**

### Deck 4 – Timed Automata

Setzt konsequent auf Deck 3 auf und erweitert es um Zeit – inhaltlich der richtige Schritt. Die schrittweise Einführung von Uhren, Guards und Invarianten ist methodisch nachvollziehbar.

**Kritik:** Der Vorausgriff auf UPPAAL (Deck 5) kommt spät. Eine kurze Folie gegen Ende von Deck 4 – „Was können wir mit diesen Modellen anfangen? Wir verifizieren sie im nächsten Deck." – würde Neugier wecken und den Übergang motivieren.

### Deck 5 – Verifikation mit UPPAAL

Die Rückbindung an Deck 4 ist explizit – das ist ein Pluspunkt. Der Praxisbezug durch das Werkzeug (UPPAAL GUI, Simulationen, Gegenbeispiele) macht die abstrakte Theorie greifbar.

**Kritik:** CTL/TCTL-Eigenschaften werden relativ direkt in formaler Syntax eingeführt. Ein zwischengelagerter Schritt – erst informale Eigenschaftsbeschreibung in natürlicher Sprache, dann Übersetzung in Formelnotation – würde den Einstieg erheblich erleichtern.

### Deck 6 – C + Rust

Das Deck ist inhaltlich wertvoll und modern, aber **didaktisch schwach eingebettet**. Nach drei Decks formaler Mathematik (Timed Automata, TCTL, Modellprüfung) wirkt der Wechsel zu Programmiersprachen abrupt. Es fehlt eine Brückenfolie: „Vom Modell zur Implementierung – wie übersetze ich ein verifiziertes Modell in Code?"

**Empfehlung:** Eine einleitende Folie mit dem Bogen „Modell → Verifikation → Implementierung" würde Deck 6 konzeptuell verankern und den Kursfluss runden.

---

## 2. Plausibilität – Fachliche Korrektheit und inhaltliche Kohärenz

### Deck 0

Die Begriffswelt (Echtzeit, Ressourcenbeschränkung, Verlässlichkeit) ist korrekt und vollständig abgedeckt. Die Abgrenzung von Embedded Systems gegenüber allgemeinen Computersystemen ist trennscharf. Architekturdiagramme (MCU, Sensoren, Aktuatoren, Kommunikationsbusse) sind technisch korrekt und praxisrelevant.

### Deck 1

Das V-Modell ist korrekt dargestellt und sinnvoll auf ES angewendet. Teststrategien (Unit, Integration, Hardware-in-the-Loop) sind realistisch und industrienah. AUTOSAR als Referenz für Softwarearchitektur in der Automobilindustrie ist zeitgemäß und fachlich gut eingebettet. Keine wesentlichen Kritikpunkte.

### Deck 2

UML-Diagrammtypen sind korrekt verwendet. Positiv hervorzuheben: Timing-Diagramme werden oft in ES-Vorlesungen vernachlässigt – ihre Aufnahme ist ein Qualitätsmerkmal.

**Kleiner Kritikpunkt:** Die Abgrenzung zwischen UML (softwareorientiert) und SysML (systemorientiert) fehlt. In der Praxis – insbesondere in der Automotive- und Aerospace-Domäne – ist SysML präsenter. Ein kurzer Hinweis würde das Bild abrunden.

### Deck 3

Mealy- und Moore-Automaten sind korrekt definiert und abgegrenzt. Harel Statecharts sind formal präzise eingeführt. Die Semantik von Hierarchie (History-States) und Orthogonalität (parallele Regionen) ist korrekt behandelt. **Fachlich das stärkste Deck der Reihe.**

### Deck 4

Timed Automata nach Alur & Dill sind vollständig und korrekt dargestellt. Uhrvariablen, Guard-Bedingungen, Invarianten und Synchronisation über Kanäle zwischen Automatennetzen sind formal präzise. Kein wesentlicher Kritikpunkt.

### Deck 5

UPPAAL ist ein industrienaher, wissenschaftlich etablierter Verifikator – eine sehr gute Werkzeugwahl. CTL/TCTL-Eigenschaften (Sicherheit, Lebendigkeit, Erreichbarkeit) sind korrekt.

**Lücke:** Die inhärenten Grenzen der formalen Verifikation – Zustandsraumexplosion, Skalierungsprobleme bei großen Systemen, Komplementarität zu Tests statt Ersatz – werden zu wenig thematisiert. Für ein vollständiges Bild sollte mindestens eine Folie zu „Wann stößt Model Checking an seine Grenzen?" vorhanden sein.

### Deck 6

Der Vergleich C vs. Rust für Embedded Systems ist fachlich fundiert und zeitgemäß. Das Rust-Ownership-Modell ist korrekt und verständlich erklärt. Bare-Metal-Programmierung mit Rust ist ein zukunftsrelevantes Thema.

**Verpasste Chance:** Rust's Typsystem bietet selbst eine Form von statischer (Typ-)Verifikation – der Bogen zu Decks 4–5 hätte gezogen werden können: „Was formale Modellprüfer global leisten, leistet Rust's Borrow Checker lokal für Speichersicherheit." Diese Brücke würde die Kohärenz der gesamten Reihe stärken.

---

## 3. Niveau – Angemessenheit für HAW (Bachelor/Master)

**Maßstab:** HAW-Niveau bedeutet: anwendungsorientiert, methodisch fundiert, mit Transfer zur Praxis. Weniger formale Beweise als an Universitäten, aber solide Fachkompetenz und Werkzeugkompetenz.

### Deck 0

Sehr gut kalibriert für einen Einstieg im 3.–4. Bachelor-Semester. Die Kombination aus alltagsnahen Beispielen und technischen Grundbegriffen ist zugänglich ohne trivial zu sein. ★★★★★

### Deck 1

Angemessen für Bachelor mit SE-Grundlagenkenntnissen. V-Modell und Testkonzepte sind auf HAW-Niveau etabliert. AUTOSAR ist komplex – für eine Erstbegegnung könnte die Einführung etwas schrittweiser gestaltet werden (weniger Detailtiefe, mehr Motivation). ★★★★☆

### Deck 2

UML ist für HAW-Studierende aus dem Grundstudium bekannt. Der ES-spezifische Fokus (Realzeitkommunikation, Timing-Diagramme, eingebettete Statecharts) hebt das Deck sinnvoll über das Grundlagenniveau hinaus, ohne zu überfordern. ★★★★☆

### Deck 3

Das Niveau steigt hier deutlich. Harel Statecharts mit Hierarchie und Orthogonalität sind für Studierende ohne formale Grundlagen eine Herausforderung. Das Deck ist gut gemacht, aber für ein reines Bachelor-Publikum ohne Vorwissen aus Theoretischer Informatik könnte die Lernkurve steil werden.

**Empfehlung:** Mehr begleitende Übungsaufgaben (z. B. als Teil des Decks oder als Aufgabenblatt) sowie gelöste Schritt-für-Schritt-Beispiele würden das Niveau für HAW-Studierende gut fassbar machen. ★★★★☆

### Deck 4

Timed Automata sind formal-mathematisch anspruchsvoll. Uhrvariablen, Invarianten und die formale Definition von Netzwerken liegen eher auf Master- oder hohem Bachelor-Niveau. Für ein reines Bachelor-Publikum ohne Grundlagen in formalen Sprachen besteht **Überforderungsgefahr**.

**Empfehlung:** Lernziele explizit differenzieren (z. B. „Bachelor: Modelle lesen und verstehen; Master: Modelle selbstständig entwerfen und verifizieren"). Mehr intuitive Einstiegsbeispiele vor dem formalen Apparat. ★★★☆☆

### Deck 5

Der Praxisbezug durch das UPPAAL-Werkzeug rettet das Niveau deutlich: Studierende können Modelle klicken, simulieren und Fehler sehen, ohne die Mathematik vollständig durchdrungen zu haben. Das ist eine gute HAW-Eigenschaft des Decks – werkzeuggestützte Vermittlung formaler Konzepte.

**Voraussetzung:** Setzt voraus, dass Deck 4 inhaltlich sitzt. Wenn Deck 4 zu anspruchsvoll war, potenziert sich das Problem in Deck 5. ★★★★☆

### Deck 6

Ausgezeichnet kalibriert für eine HAW. C ist bekannt, Rust ist modern und industriell aufstrebend. Bare-Metal-Programmierung ist praxisnah und für Embedded-Ingenieure direkt verwertbar. Das Deck hat das stärkste Anwendungsprofil der gesamten Reihe. ★★★★★

---

## 4. Gesamtbewertung und Top-Empfehlungen

Die Vorlesungsreihe ist insgesamt **sehr solide** – fachlich korrekt, thematisch zeitgemäß und mit einem klaren inhaltlichen Aufbau. Die formale Sequenz (Decks 3–5) ist ein Highlight und zeigt, dass theoretisch anspruchsvolle Inhalte didaktisch sinnvoll aufgebaut werden können. Folgende Punkte würden die Reihe weiter stärken:

**1. Deck 0 straffen**
55+ Folien für eine Einführungsvorlesung sind zu viel. Empfehlung: auf ~35 Folien reduzieren, Detailinhalte in thematisch passendere Decks verschieben.

**2. Grafische Kursroadmap einbauen**
Eine Überblicksfolie am Ende von Deck 0 – mit allen Decks, ihren Themen und inhaltlichen Abhängigkeiten – gibt Studierenden Orientierung für das gesamte Semester.

**3. Deck 6 besser einbetten**
Eine Brückenfolie am Anfang von Deck 6 mit dem Bogen „Vom verifizierten Modell zur Implementierung" klärt, warum C/Rust jetzt Thema ist – und schließt den Kreis zur formalen Verifikation.

**4. Deck 4 Niveau überprüfen / Lernziele differenzieren**
Explizit ausweisen, was Bachelor-Studierende und was Master-Studierende aus diesem Deck mitnehmen sollen. Mehr intuitive Einstiegsbeispiele vor der formalen Notation.

**5. Grenzen der Verifikation in Deck 5 thematisieren**
Zustandsraumexplosion, Skalierbarkeit großer Systeme und die Komplementarität zu Tests (nicht: Ersatz) gehören zu einem vollständigen Bild formaler Methoden.

**6. Rust–Verifikation-Bogen in Deck 6 ziehen**
„Rust's Borrow Checker als statische lokale Verifikation" ist ein eleganter Abschluss der gesamten Reihe und verbindet Decks 4–5 mit Deck 6 auf inhaltlicher Ebene.

---

*Bewertung erstellt auf Basis der Folien 1–20 je Deck (Decks 0–6). Deck 7 (ROS) wurde bewusst ausgeschlossen.*
