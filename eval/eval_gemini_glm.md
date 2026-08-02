# Evaluation: gemini_glm vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 357/388 (92.0%)**
- Exact-key matches: 300; fuzzy-only matches: 57
- Date agreement (matched pairs, both dated): 252/357 (70.6%)
- Content-type agreement (type-blind matches): 356/356 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 311/357 (87.1%)
- Missed Willis rows: 31
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 78

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 323 | 350 | 92.3% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 28 | 30 | 93.3% |
| team information | 2 | 4 | 50.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Mr. Haviland's XI v Luton Villa Road | 18950803 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 18 | Reading v Marylebone | 18950805 | match information |
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
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 53 | Langley v Crossley's | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane | 0.812 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | T W Girdlestone's XI v Girdlestoneites | 0.818 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 51 | Bollington v Sandbach | Bollington First XI v Sandbach | 0.824 |
| 14 | All Saints' v Boys' Brigade | All Saints' v Boys' Brigade Second XI | 0.833 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 56 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 57 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 42 | Assistants v Professors and Demonstrators | New Museums Professors And Demonstrators v Assistants | 0.872 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Leyd-Shulme | 0.885 |
| 54 | Worcestershire v Cheshire | Cheshire v Worcester | 0.889 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Wynne's XI v Griffith's XI | 0.889 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 34 | Colman Green v Gerrards Cross | Colesh Green v Gerrards Cross | 0.897 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 49 | Mr G H Ling's XI v Cheadle | GH Ling's XI v Cheadle | 0.913 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory Second XI v White Cross (basingstoke) | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 59 | Birkenhead Park A player statistics | Birkenhead Park A Team player statistics | 0.933 |
| 53 | Lancashire Hill v Harpurhey Wesleyans | Lancashire-Hill SS v Harpurhey Wesleyans | 0.935 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 56 | Chorlton A Team v Macclesfield Conservative Club | Chorlton A Team v Macclesfield Conservative | 0.945 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton A Team v Macclesfield Conservative | 0.945 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Haviland's XI v Luton Villa-Road | 18950803 | match information |
| 4 | Houghton Married v Houghton Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's, Luton | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of Third Volunteer Battalion | 18950807 | match information |
| 13 | Married v Single | 18950518 | match information |
| 16 | Reading School player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 18 | Reading v MCC | 18950800 | match information |
| 18 | Sunningdale School team aggregates | 18950000 | statistics |
| 19 | Sunningdale School team aggregates | 18950000 | statistics |
| 24 | Abingdon team aggregates | 18950000 | statistics |
| 25 | Newbury team aggregates | 18950000 | statistics |
| 26 | Burghclere v Newtown | 18950000 | match information |
| 26 | Speen team aggregates | 18950000 | statistics |
| 26 | Stockcross team aggregates | 18950000 | statistics |
| 27 | 49th Regimental District team aggregates | 18950000 | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 29 | Lechlade annual dinner | 18951031 | organisation information |
| 29 | Lechlade team aggregates | 18950000 | statistics |
| 30 | Maidenhead team aggregates | 18950000 | statistics |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 34 | Wycombe Marsh FC organisation information | 18950730 | organisation information |
| 35 | Parish Church v Fenny Stratford S Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 39 | H Penton's XI v Hedgerley Home | 18950822 | match information |
| 40 | Hoare's Sutton XI v Haddenham XII | 18950727 | match information |
| 41 | Histon And Impington v Old Higher Grade | 18950727 | match information |
| 43 | KS Ranjitsinhji | 18950000 | biography |
| 43 | Leading Batsmen Averages | 18950804 | statistics |
| 48 | Garston v Liverpool Second XI | 18950000 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950000 | match information |
| 50 | G H Ling's XI v Cheadle | 18950727 | match information |
| 50 | Lancashire Hill S S v Haughton Wesleyans First XI | 18950727 | match information |
| 50 | Macclesfield v Poynton | 18950727 | match information |
| 50 | Phoenix v Manchester South End | 18950727 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950727 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950727 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Strines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950727 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950000 | match information |
| 51 | Hanover First XI v Heywood's Excelsior First XI | 18950000 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950000 | match information |
| 51 | Kersal v Heaton Mersey | 18950000 | match information |
| 51 | Phoenix v Martretez | 18950000 | match information |
| 51 | Stockport v Great Moor | 18950810 | match information |
| 52 | Bollington First XI v Bugsworth | 18950800 | match information |
| 52 | Phoenix v Martirires | 18950800 | match information |
| 52 | Stockport v Great Moor | 18950803 | match information |
| 53 | Langley v Sutton | 18950817 | match information |
| 54 | Birkenhead Advertiser | 18950817 | newspaper cuttings |
| 54 | Bromborough Pool v Police First XI | 18950817 | match information |
| 54 | Park v Ormskirk | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 55 | All Saints' v Tranmere Wesley | 18950817 | match information |
| 55 | Bebington Bible Class v St John's Second XI | 18950817 | match information |
| 57 | Middlesex v Lancashire | 18950000 | match information |
| 59 | Rock Ferry Second XI player statistics | 18950900 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950000 | statistics |
| 61 | Birkenhead Victoria players | 18950000 | player information |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950000 | statistics |
| 61 | Oxton players | 18950000 | player information |
| 61 | Parkites (Birkenhead Park) player statistics | 18950000 | statistics |
| 61 | Parkites (Birkenhead Park) players | 18950000 | player information |
| 61 | Rock Ferry player statistics | 18950000 | statistics |
| 61 | Rock Ferry players | 18950000 | player information |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
