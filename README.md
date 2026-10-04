# Schoolverlaters analyse

Dit project analyseert gegevens van schoolverlaters.

## Dataset

De dataset bevat informatie over:

- Opleidingsniveau-
- Geslacht
- Oordeel keuzemogelijkheden
- Oordeel moeilijkheidsgraad
- Arbeidsuren_per_week
- Bruto_maandinkomen
- Leeftijd
- Gaan doen na vmbo
- Opleidingsniveau moeder
- Opleidingsniveau vader
- Oordeel aansluiting
- Vervolgopleiding nog steeds volgen

## Uitvoeren

Installeer de benodigde packages:

pip install -r requirements.txt

Voer daarna uit:

```powershell
python main.py
```

## Posterfiguren: aansluiting

De twee figuren voor het oordeel over de aansluiting tussen opleidingen worden
gemaakt met pandas en matplotlib. Voer vanaf de projectmap uit:

```powershell
python scripts/genereer_grafieken.py
```

Het script leest `data/raw/Schoolverlaters dataset.csv` (puntkomma-gescheiden,
UTF-8-SIG) en wijzigt de brondata niet. De gebruikte kolommen zijn
`Vragenlijstnummer` en `Oordeel aansluiting`. In de bron zijn de antwoorden
opgeslagen als tekstlabels: `vmbo` en `havo of vwo`, en `slecht`, `matig`,
`redelijk` en `goed`. De categorievolgorde van het oordeel is slecht, matig,
redelijk, goed. De markering `*` geldt als ontbrekende waarde.

Het script maakt de volgende bestanden aan:

- `figuren/aansluiting_totaal.png`: totale verdeling in percentages.
- `figuren/aansluiting_onderwijsniveau.png`: 100%-gestapelde vergelijking tussen vmbo en havo/vwo.
- `resultaten/aansluiting_frequenties_percentages.csv`: frequenties en percentages per categorie en groep, met groepssamenvattingen.
- `resultaten/aansluiting_samenvatting.txt`: leesbare samenvatting, mediaan, redelijk/goed-percentages en datacontroles.

De PNG-bestanden worden op 300 dpi opgeslagen. Het script controleert dat de
percentages per groep en totaal optellen tot 100% (binnen afronding) en
rapporteert ontbrekende of onbekende waarden in de samenvatting.

### Uitkomsten huidige dataset

Van de 3.690 rijen hadden 3.274 een geldig oordeel; 416 rijen zijn uitgesloten
omdat het oordeel ontbreekt (`*`). Er ontbraken geen onderwijsniveaus en er
werden geen andere/onbekende labels aangetroffen.

| Onderwijsgroep | Geldig n | Mediaan oordeel | Redelijk of goed |
| --- | ---: | --- | ---: |
| Totaal | 3.274 | - | 78,10% |
| vmbo | 2.476 | Redelijk | 76,78% |
| havo/vwo | 798 | Redelijk | 82,21% |

Het percentage redelijk/goed ligt bij havo/vwo 5,43 procentpunt hoger dan bij
vmbo. De totale verdeling is: slecht 4,76%, matig 17,14%, redelijk 37,54% en
goed 40,56%. De CSV- en TXT-bestanden bevatten de volledige frequenties en
aanvullende resultaten.
