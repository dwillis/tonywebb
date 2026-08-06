# Evaluation: sonnet46_reconciled vs Willis ground truth

Willis pages covered: 57 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 360/395 (91.1%)**
- Exact-key matches: 293; fuzzy-only matches: 67
- Date agreement (matched pairs, both dated): 300/360 (83.3%)
- Content-type agreement (type-blind matches): 364/364 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 286/360 (79.4%)
- Missed Willis rows: 35
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 97

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 328 | 358 | 91.6% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 25 | 30 | 83.3% |
| team information | 3 | 3 | 100.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Haviland's XI v Luton Villa Road | 18950803 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | 18950727 | match information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 18 | Reading v Marylebone | 18950805 | match information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 34 | Wycombe v Oriel | 18950806 | match information |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 39 | Master H Penton's XI v Hedgerley Home | 18950822 | match information |
| 39 | W Pearce's (Wycombe) XI v Southall | 18950824 | match information |
| 40 | Sutton v Haddenham | 18950727 | match information |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 42 | Assistants v Professors and Demonstrators | 18950810 | match information |
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
| 59 | Birkenhead Victoria First XI player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |
| 60 | Oxton Second XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry Second XI player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane | 0.812 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | T W Girdlestone's XI v Girdlestoneites | 0.818 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 34 | Chalfont Park v St. Silas (London) | Chalfont Park v St Silas | 0.842 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 4 | Houghton Married v Single | Houghton Married v Houghton Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 34 | Burnham v Postal Telegraph (London) | Burnham v Postal Telegraph | 0.852 |
| 59 | Birkenhead Park A player statistics | Birkenhead Victoria player statistics | 0.861 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Beethoven | 0.866 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Wynne's XI v Griffith's XI | 0.889 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancashire Hill SS v Haughton Wesleyans | 0.897 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 3 | Sewers Lime Works v Blows Down Lime Works | Sowell Lime Works v Blows Down Lime Works | 0.927 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 53 | Lancashire Hill v Harpurhey Wesleyans | Lancashire-Hill SS v Harpurhey Wesleyans | 0.935 |
| 49 | Mr G H Ling's XI v Cheadle | G H Ling's XI v Cheadle | 0.936 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 56 | Chorlton A Team v Macclesfield Conservative Club | Chorlton A Team v Macclesfield Conservative | 0.945 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | R H Haviland's XI v Luton Villa-Road | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 8 | Luton Volunteers v Rest Of Battalion | 18950810 | match information |
| 14 | All Saints' v Boys' Brigade First Wokingham Company Second XI | 18950518 | match information |
| 15 | Earley St Peter's | 18950518 | team information |
| 16 | Reading School player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 17 | Biscuit Factory Second XI v White Cross | 18950727 | match information |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Reading v MCC | 18950803 | match information |
| 18 | Sunningdale School team aggregates | 18950000 | statistics |
| 19 | T W Girdlestone's XI team aggregates | 18950000 | statistics |
| 24 | Abingdon team aggregates | 18950000 | statistics |
| 25 | Newbury team aggregates | 18950000 | statistics |
| 26 | Burghclere v Newtown | 18950000 | match information |
| 26 | Speen team aggregates | 18950000 | statistics |
| 26 | Stockcross team aggregates | 18950907 | statistics |
| 27 | 49th Regimental District team aggregates | 18950000 | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 29 | Lechlade | 18951031 | team information |
| 29 | Lechlade team aggregates | 18950000 | statistics |
| 30 | Maidenhead team aggregates | 18950000 | statistics |
| 32 | Church Room | 18950000 | team information |
| 32 | St John's | 18950000 | team information |
| 32 | Wycombe YMCA | 18950000 | team information |
| 33 | Saturday's Fixtures match list | 18950803 | team information |
| 33 | Wooburn | 18950803 | team information |
| 34 | Gerrards Cross v Osborne Stevens And Co | 18950731 | match information |
| 34 | High Wycombe v Oriel | 18950806 | match information |
| 34 | Wycombe Marsh FC | 18950730 | team information |
| 35 | Parish Church v Fenny Stratford St Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton | 18950805 | match information |
| 39 | H Penton's XI v Hedgerley Home | 18950822 | match information |
| 39 | W Pearce's XI v Southall Gas Works | 18950824 | match information |
| 40 | Hoare's Sutton XI v Haddenham XII | 18950727 | match information |
| 41 | Histon And Impington v Old Higher Grade | 18950727 | match information |
| 42 | New Museums Professors And Demonstrators v New Museums Assistants | 18950810 | match information |
| 43 | K S Ranjitsinhji | 18950000 | biography |
| 48 | Garston v Liverpool Second XI | 18950000 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | G H Ling's XI v Cheadle | 18950727 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans | 18950727 | match information |
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
| 52 | Phoenix v Marterers | 18950810 | match information |
| 52 | Stockport v Great Moor | 18950810 | match information |
| 54 | Park v Ormskirk | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 55 | All Saints | 18950800 | team information |
| 56 | St Thomas' Athletic | 18950000 | team information |
| 57 | Middlesex v Lancashire | 18950000 | match information |
| 57 | Phoenix Second XI v Moseley Second XI | 18950824 | match information |
| 57 | St Thomas' Athletic | 18950831 | team information |
| 58 | Birkenhead Victoria team aggregates | 18950000 | statistics |
| 58 | Formby team aggregates | 18950000 | statistics |
| 58 | Liverpool team aggregates | 18950000 | statistics |
| 58 | Northern team aggregates | 18950000 | statistics |
| 58 | Prescot team aggregates | 18950000 | statistics |
| 59 | Birkenhead Park team aggregates | 18950000 | statistics |
| 59 | Birkenhead Victoria team aggregates | 18950000 | statistics |
| 59 | Fixtures For To-Day match list | 18950914 | team information |
| 59 | Oxton team aggregates | 18950000 | statistics |
| 59 | Rock Ferry team aggregates | 18950000 | statistics |
| 59 | St Aidan's team aggregates | 18950000 | statistics |
| 60 | Birkenhead Park team aggregates | 18950000 | statistics |
| 60 | Birkenhead Victoria team aggregates | 18950000 | statistics |
| 60 | Oxton team aggregates | 18950000 | statistics |
| 60 | Rock Ferry team aggregates | 18950000 | statistics |
| 61 | Birkenhead Park player statistics | 18950000 | statistics |
| 61 | Birkenhead Park team aggregates | 18950000 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950000 | statistics |
| 61 | Birkenhead Victoria team aggregates | 18950000 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950000 | statistics |
| 61 | Oxton team aggregates | 18950000 | statistics |
| 61 | Rock Ferry player statistics | 18950000 | statistics |
| 61 | Rock Ferry team aggregates | 18950000 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
