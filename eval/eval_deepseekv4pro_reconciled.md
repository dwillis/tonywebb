# Evaluation: deepseekv4pro_reconciled vs Willis ground truth

Willis pages covered: 57 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 358/395 (90.6%)**
- Exact-key matches: 309; fuzzy-only matches: 49
- Date agreement (matched pairs, both dated): 297/358 (83.0%)
- Content-type agreement (type-blind matches): 362/362 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 285/358 (79.6%)
- Missed Willis rows: 37
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 83

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 329 | 358 | 91.9% |
| newspaper cuttings | 1 | 2 | 50.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 23 | 30 | 76.7% |
| team information | 3 | 3 | 100.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Haviland's XI v Luton Villa Road | 18950803 | match information |
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 24 | Abingdon player statistics | 18950000 | statistics |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Biscuit Factory team aggregates | 18950000 | statistics |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 41 | Cambridge | 18950803 | newspaper cuttings |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 48 | Garston v Liverpool 3rd | 18950700 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Cheadle v Heaton Mersey | 18950810 | match information |
| 51 | Hazel Grove UC v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Phoenix v Manchester | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 54 | Mr Wynne's XI v Mr Griffith's XI | 18950817 | match information |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | 18950824 | match information |
| 56 | Reddish Vale v Mr R P Hammond's Team | 18950824 | match information |
| 57 | Reddish Vale v Mr R P Hammond's Team | 18950824 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |
| 60 | Oxton Second XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry Second XI player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | T W Girdlestone's XI v Girdlestoneites | 0.818 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 42 | Assistants v Professors and Demonstrators | New Museums Professors & Demonstrators v Assistants | 0.826 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 34 | Chalfont Park v St. Silas (London) | Chalfont Park v St Silas | 0.842 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 34 | Burnham v Postal Telegraph (London) | Burnham v Postal Telegraph | 0.852 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 49 | Mr G H Ling's XI v Cheadle | GH Ling's XI v Cheadle | 0.913 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 56 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservative Club | 0.921 |
| 3 | Sewers Lime Works v Blows Down Lime Works | Sowell Lime Works v Blows Down Lime Works | 0.927 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 53 | Lancashire Hill v Harpurhey Wesleyans | Lancashire-Hill SS v Harpurhey Wesleyans | 0.935 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Lever-Shulme | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 53 | Langley v Crossley's | Langley v Crosley | 0.944 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | R H Haviland's XI v Luton Villa-Road | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 8 | Luton Volunteers v Rest Of Battalion | 18950810 | match information |
| 11 | Town Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade (first Wokingham Company) Second XI | 18950518 | match information |
| 15 | Earley St Peter's | 18950518 | team information |
| 16 | Reading School player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 24 | Abingdon Cricket and Football Club player statistics | 18950000 | statistics |
| 25 | Newbury team aggregates | 18950000 | statistics |
| 26 | Burghclere v Newtown | 18950900 | match information |
| 29 | Lechlade team aggregates | 18950000 | statistics |
| 32 | Church Room CC match list | 18950719 | team information |
| 32 | Grammar School Past And Present v Wycombe Club | 18950718 | match information |
| 32 | St John's | 18950719 | team information |
| 32 | St John's CC match list | 18950719 | team information |
| 32 | Wycombe First XI match list | 18950719 | team information |
| 32 | Wycombe Reserves match list | 18950719 | team information |
| 32 | Wycombe YMCA match list | 18950719 | team information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 34 | Wycombe Marsh FC | 18950730 | team information |
| 34 | Wycombe YMCA match list | 18950803 | team information |
| 35 | Parish Church v Fenny Stratford S Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton | 18950805 | match information |
| 41 | Cambridgeshire v Huntingdonshire | 18950731 | match information |
| 41 | Cambridgeshire v MCC And Ground | 18950727 | match information |
| 41 | Histon And Impington v Old Higher Grade | 18950727 | match information |
| 41 | Old Higher Grade v Sawston | 18950727 | match information |
| 43 | KS Ranjitsinhji | 18950800 | biography |
| 48 | Garston v Liverpool Second XI | 18950700 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | GH Ling's XI v Cheadle | 18950727 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First XI | 18950727 | match information |
| 50 | Macclesfield v Poynton | 18950727 | match information |
| 50 | Phoenix v Manchester South End | 18950727 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950727 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950727 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Strines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950727 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Kersal v Heaton Mersey | 18950810 | match information |
| 51 | Phoenix v Martretes | 18950810 | match information |
| 51 | Poynton v Great Moor | 18950810 | match information |
| 52 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 52 | Hanover First XI v Heywood's Excelsior First XI | 18950810 | match information |
| 52 | Phoenix v Marterers | 18950810 | match information |
| 52 | Stockport v Great Moor | 18950810 | match information |
| 54 | Bromborough Pool v Police | 18950817 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 54 | Wynne's Team v Griffith's Team | 18950817 | match information |
| 55 | All Saints | 18950800 | team information |
| 55 | Bebington Bible Class v St John's Second XI | 18950817 | match information |
| 56 | Cheetham v Levenshulme | 18950800 | match information |
| 56 | Reddish Vale v RP Hammond's Team | 18950824 | match information |
| 56 | St Thomas' Athletic | 18950800 | team information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Reddish Vale v RP Hammond's Team | 18950824 | match information |
| 57 | St Thomas' Athletic | 18950831 | team information |
| 59 | Birkenhead St Mary's match list | 18950914 | team information |
| 59 | Bromborough Pool match list | 18950914 | team information |
| 59 | Mersey Second XI match list | 18950914 | team information |
| 59 | Oxton A match list | 18950914 | team information |
| 59 | Oxton Extra match list | 18950914 | team information |
| 59 | St John's A match list | 18950914 | team information |
| 59 | Tranmere Wesley match list | 18950914 | team information |
| 61 | Birkenhead Park player statistics | 18950000 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950000 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950000 | statistics |
| 61 | Rock Ferry player statistics | 18950000 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
