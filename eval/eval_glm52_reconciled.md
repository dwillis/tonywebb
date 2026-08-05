# Evaluation: glm52_reconciled vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 324/388 (83.5%)**
- Exact-key matches: 266; fuzzy-only matches: 58
- Date agreement (matched pairs, both dated): 280/324 (86.4%)
- Content-type agreement (type-blind matches): 325/326 (99.7%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 282/324 (87.0%)
- Missed Willis rows: 64
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 57

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 300 | 350 | 85.7% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 20 | 30 | 66.7% |
| team information | 0 | 4 | 0.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Mr. Haviland's XI v Luton Villa Road | 18950803 | match information |
| 8 | Houghton v Westoning | 18950815 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 16 | Reading School match list | 18950802 | team information |
| 18 | Reading v Marylebone | 18950805 | match information |
| 25 | Newbury match list | 18950000 | team information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 26 | Stockcross match list | 18950000 | team information |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 39 | Master H Penton's XI v Hedgerley Home | 18950822 | match information |
| 40 | Sutton v Haddenham | 18950727 | match information |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 48 | Garston v Liverpool 3rd | 18950700 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Cheadle v Heaton Mersey | 18950810 | match information |
| 51 | Hazel Grove UC v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Phoenix v Manchester | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Bollington v Sandbach | 18950810 | match information |
| 52 | Bramall 1st XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | 18950810 | match information |
| 52 | Hazel Grove v Hazel Grove Tradesmen | 18950810 | match information |
| 52 | Kersal v Heaton Mersey | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 52 | St Joseph's (Reddish) v St Thomas' (Hyde) | 18950810 | match information |
| 52 | Stockport v Little Lever | 18950810 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 55 | Helsby v Port Sunlight | 18950817 | match information |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | 18950817 | match information |
| 55 | Neston and District v Kirkdale Wesleyans | 18950817 | match information |
| 55 | Oxton v Huyton | 18950817 | match information |
| 55 | Spital v Boughton Hall | 18950817 | match information |
| 55 | Woodland v Kingsley | 18950819 | match information |
| 57 | Bollington v Fairfield | 18950824 | match information |
| 57 | Didsbury 2nd XI v Poynton 2nd XI | 18950824 | match information |
| 57 | Didsbury v Poynton | 18950824 | match information |
| 57 | Lads' Club 2nd XI v St Thomas' Athletic | 18950824 | match information |
| 57 | Reddish Vale v Mr R P Hammond's Team | 18950824 | match information |
| 57 | Seymour Mead's v Stockport Post Office | 18950821 | match information |
| 57 | Stockport 2nd XI v Cheadle Hulme 2nd XI | 18950824 | match information |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | 18950824 | match information |
| 57 | Stockport v Cheadle Hulme | 18950824 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |
| 59 | Birkenhead Victoria First XI player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |
| 60 | Birkenhead Park First XI player statistics | 18950901 | statistics |
| 60 | Birkenhead Victoria First XI player statistics | 18950901 | statistics |
| 60 | Oxton First XI player statistics | 18950901 | statistics |
| 60 | Oxton Second XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry First XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry Second XI player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 52 | Hanover 2nd XI v Heywood's Excelsior 2nd XI | Hanover First XI v Heywood's Excelsior First XI | 0.809 |
| 55 | Liverpool v Rock Ferry | Liverpool v Rock Ferry Second XI | 0.815 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall v Stockport Second XI | 0.853 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservative | 0.857 |
| 56 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Beethoven | 0.866 |
| 42 | Assistants v Professors and Demonstrators | New Museums Professors And Demonstrators v Assistants | 0.872 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Wynne's XI v Griffith's XI | 0.889 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 49 | Mr G H Ling's XI v Cheadle | GH Ling's XI v Cheadle | 0.913 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 53 | Lancashire Hill v Harpurhey Wesleyans | Lancashire-Hill S S v Harpurhey Wesleyans | 0.923 |
| 3 | Sewers Lime Works v Blows Down Lime Works | Sowell Lime Works v Blows Down Lime Works | 0.927 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory Second XI v White Cross (basingstoke) | 0.931 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Lever-Shulme | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Haviland's XI v Luton Villa Road | 18950803 | match information |
| 7 | Luton Detachment v Remainder Of Third Volunteer Battalion | 18950807 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade First Wokingham Company Second XI | 18950518 | match information |
| 16 | Reading School player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 18 | Reading v MCC | 18950803 | match information |
| 24 | Abingdon team aggregates | 18950000 | statistics |
| 25 | Newbury team aggregates | 18950000 | statistics |
| 26 | Burghclere v Newtown | 18950000 | match information |
| 26 | Newtown team aggregates | 18950000 | statistics |
| 26 | Stockcross team aggregates | 18950000 | statistics |
| 27 | 49th Regimental District team aggregates | 18950000 | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 29 | Lechlade annual dinner | 18951031 | newspaper cuttings |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 35 | Parish Church v Fenny Stratford S Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 39 | H Penton's XI v Hedgerley Home | 18950822 | match information |
| 40 | Hoare's Sutton XI v Haddenham XII | 18950727 | match information |
| 41 | Histon And Impington v Old Higher Grade | 18950727 | match information |
| 43 | KS Ranjitsinhji | 18950000 | biography |
| 48 | Garston v Liverpool Second XI | 18950700 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | G H Ling's XI v Cheadle | 18950727 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Kersal v Heaton Mersey | 18950810 | match information |
| 51 | Phoenix v Martretes | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950810 | match information |
| 52 | Phoenix v Marterers | 18950810 | match information |
| 54 | Bromborough Pool v Birkenhead Victoria | 18950817 | newspaper cuttings |
| 54 | Bromborough Pool v Police First XI | 18950817 | match information |
| 54 | Park v Ormskirk | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 55 | All Saints' v Wesleyites | 18950817 | match information |
| 57 | Middlesex v Lancashire | 18950000 | match information |
| 57 | Phoenix Second XI v Moseley Second XI | 18950824 | match information |
| 59 | Birkenhead Park team aggregates | 18950000 | statistics |
| 59 | Birkenhead Victoria team aggregates | 18950000 | statistics |
| 59 | Oxton team aggregates | 18950000 | statistics |
| 59 | Rock Ferry Second XI player statistics | 18950000 | statistics |
| 59 | Rock Ferry Second XI team aggregates | 18950000 | statistics |
| 59 | Rock Ferry team aggregates | 18950000 | statistics |
| 59 | St Aidan's team aggregates | 18950000 | statistics |
| 61 | Birkenhead Park player statistics | 18950907 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950907 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950907 | statistics |
| 61 | Rock Ferry player statistics | 18950907 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
