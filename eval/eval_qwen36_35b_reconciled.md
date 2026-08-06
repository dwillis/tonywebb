# Evaluation: qwen36_35b_reconciled vs Willis ground truth

Willis pages covered: 57 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 359/395 (90.9%)**
- Exact-key matches: 274; fuzzy-only matches: 85
- Date agreement (matched pairs, both dated): 298/359 (83.0%)
- Content-type agreement (type-blind matches): 355/355 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 310/359 (86.4%)
- Missed Willis rows: 36
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 80

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 326 | 358 | 91.1% |
| newspaper cuttings | 1 | 2 | 50.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 27 | 30 | 90.0% |
| team information | 3 | 3 | 100.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 22 | Gentlemen Of Berkshire v CD Rose's XI | 18950817 | match information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 38 | Marlow v J Monro Walker's XI | 18950824 | match information |
| 40 | Sutton v Haddenham | 18950727 | match information |
| 41 | Cambridge | 18950803 | newspaper cuttings |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 48 | Garston v Liverpool 3rd | 18950700 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Bramall 2nd XI v Stockport 2nd XI | 18950810 | match information |
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
| 55 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | 18950824 | match information |
| 57 | Stockport 2nd XI v Cheadle Hulme 2nd XI | 18950824 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 39 | Four Veterans v Four Juniors | Four Veterans v Four Juniors Single Wicket | 0.8 |
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 14 | All Saints' v Boys' Brigade | All Saints' v Boys' Brigade Second XI | 0.833 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 40 | Married v Single | XI Married v XI Single | 0.842 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 59 | Bootle v Birkenhead Victoria | Bootle v Birkenhead Victoria First XI | 0.862 |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | Liverpool v Rock Ferry Second XI | 0.865 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 42 | Assistants v Professors and Demonstrators | New Museums Professors And Demonstrators v Assistants | 0.872 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 60 | Oxton Second XI player statistics | Oxton Second Eleven player statistics | 0.886 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second v Stockport Lads' Club First | 0.887 |
| 54 | Worcestershire v Cheshire | Cheshire v Worcester | 0.889 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill SS Second XI v Harpurhey Wesleyans Second XI | 0.891 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry First Eleven player statistics | 0.897 |
| 22 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton Athletic | 0.905 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 22 | Biscuit Factory A XI v Wokingham | Biscuit Factory v Wokingham | 0.915 |
| 59 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria First Eleven player statistics | 0.917 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory B XI v Causton's Athletic London | 0.92 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First | 0.92 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservative Club | 0.921 |
| 3 | Sewers Lime Works v Blows Down Lime Works | Sowell Lime Works v Blows Down Lime Works | 0.927 |
| 50 | Reddish St Joseph's v Union Street Hyde | Reddish St Joseph's v Union Street | 0.93 |
| 55 | St Mary's 2nd XI v Tranmere Wesley 2nd XI | St Mary's Second v Tranmere Wesley Second | 0.93 |
| 61 | Rock Ferry 2nd XI v Cheadle Hulme 2nd XI | Rock Ferry Second v Cheadle Hulme Second | 0.93 |
| 4 | Haviland's XI v Luton Villa Road | Haviland v Luton Villa Road | 0.931 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone XI player statistics | 0.933 |
| 51 | Hanover 2nd XI v Heywood's Excelsior 2nd XI | Hanover Second v Heywood's Excelsior Second | 0.933 |
| 23 | Sutton's Juniors v P. Sutton's XI | Sutton's Juniors v Mr P Sutton XI | 0.935 |
| 53 | Lancashire Hill v Harpurhey Wesleyans | Lancashire-Hill SS v Harpurhey Wesleyans | 0.935 |
| 49 | Mr G H Ling's XI v Cheadle | G H Ling's XI v Cheadle | 0.936 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 26 | Speen player statistics | Speen CC player statistics | 0.939 |
| 39 | Collins' Class v Booker Temperance | Mr Collinss Class v Booker Temperance | 0.943 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Lever-Shulme | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 53 | Langley v Crossley's | Langley v Crosley | 0.944 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 7 | Houghton v Westoning | 18950812 | match information |
| 8 | Luton Volunteers v Rest Of Battalion | 18950810 | match information |
| 11 | Town Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores v Single | 18950518 | match information |
| 15 | Earley St. Peter's | 18950524 | team information |
| 16 | Reading School player statistics | 18950000 | statistics |
| 16 | Reading School team aggregates | 18950000 | statistics |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 19 | Mr T W Girdlestone XI team aggregates | 18950000 | statistics |
| 22 | Gentlemen Of Berkshire v Mr C D Rose XI | 18950817 | match information |
| 24 | Abingdon team aggregates | 18950000 | statistics |
| 25 | Newbury players | 18950000 | player information |
| 25 | Newbury team aggregates | 18950000 | statistics |
| 26 | Burghclere v Newtown | 18950000 | match information |
| 26 | Newtown team aggregates | 18950000 | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 29 | Lechlade | 18951031 | team information |
| 29 | Lechlade team aggregates | 18950000 | statistics |
| 32 | Church Room CC match list | 18950720 | team information |
| 32 | St John's CC match list | 18950720 | team information |
| 32 | Wycombe YMCAC match list | 18950720 | team information |
| 33 | Saturday Fixtures | 18950803 | team information |
| 34 | Gerrards Cross v Osborne Stevens And Co | 18950731 | match information |
| 34 | Wycombe YMCA team aggregates | 18950805 | statistics |
| 35 | Parish Church v Fenny Stratford S Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 38 | Marlow v Mr J Monro Walker XI | 18950824 | match information |
| 40 | Mr Hoare's XI v Haddenham | 18950727 | match information |
| 41 | Cambridgeshire County v Huntingdonshire | 18950731 | match information |
| 41 | Gossip upon current sports and pastimes | 18950800 | newspaper cuttings |
| 41 | Histon And Impington v Old Higher Grade Second XI | 18950727 | match information |
| 41 | Old Higher Grade v Sawston | 18950727 | match information |
| 43 | K S Ranjitsinhji | 18950000 | biography |
| 48 | Garston v Liverpool Second XI | 18950700 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | G H Ling's XI v Cheadle | 18950727 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First | 18950727 | match information |
| 50 | Macclesfield v Poynton | 18950727 | match information |
| 50 | Phoenix v Manchester South End | 18950727 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950727 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950727 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Strines | 18950727 | match information |
| 50 | Stockport v Castleton | 18950727 | match information |
| 50 | Urmston v Bramall | 18950727 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 51 | Bramall First v Stockport Second | 18950810 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Kersal v Heaton Mersey | 18950810 | match information |
| 51 | Phoenix v Martretes | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950810 | match information |
| 52 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 52 | Phoenix v Marterers | 18950810 | match information |
| 52 | Stockport v Great Moor | 18950810 | match information |
| 54 | Park v Ormskirk | 18950818 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Police v Brombro Pool | 18950817 | match information |
| 54 | Port Sunlight v Helsby | 18950823 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Wynne's Team v Griffith's Team | 18950817 | match information |
| 55 | St John's Second v Bebington Bible Class | 18950817 | match information |
| 56 | St Thomas' Athletic club notice | 18950831 | team information |
| 57 | Cheetham v Levenshulme Second Elevens | 18950000 | match information |
| 57 | Middlesex v Lancashire | 18950000 | match information |
| 57 | St Thomas' Athletic team information | 18950831 | team information |
| 59 | Birkenhead St Marys match list | 18950914 | team information |
| 59 | Oxton match list | 18950914 | team information |
| 59 | Rock Ferry team aggregates | 18950000 | statistics |
| 59 | Tranmere Wesley match list | 18950914 | team information |
| 61 | Birkenhead Park player statistics | 18950907 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950907 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950907 | statistics |
| 61 | Rock Ferry player statistics | 18950907 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
