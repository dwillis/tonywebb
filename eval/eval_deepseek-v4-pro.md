# Evaluation: deepseek-v4-pro vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 349/388 (89.9%)**
- Exact-key matches: 244; fuzzy-only matches: 105
- Date agreement (matched pairs, both dated): 244/345 (70.7%)
- Content-type agreement (type-blind matches): 346/346 (100.0%)
- Missed Willis rows: 39
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 90

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 317 | 350 | 90.6% |
| newspaper cuttings | 0 | 2 | 0.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 27 | 30 | 90.0% |
| team information | 3 | 4 | 75.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 24 | Abingdon player statistics | 18950000 | statistics |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Biscuit Factory team aggregates | 18950000 | statistics |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 37 | Stokenchurch v Skirmett | 18950806 | match information |
| 39 | Four Veterans v Four Juniors | 18950826 | match information |
| 40 | Sawston v Old Higher Grade | 18950727 | match information |
| 41 | Cambridge | 18950803 | newspaper cuttings |
| 42 | Assistants v Professors and Demonstrators | 18950810 | match information |
| 43 | Cambridge | 18950810 | newspaper cuttings |
| 43 | County of Cambridge Police v Borough Police | 18950803 | match information |
| 48 | Garston v Liverpool 3rd | 18950700 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Macclesfield v Levenshulme | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 51 | St Joseph's (Reddish) v St Thomas' (Hyde) | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 53 | Lancashire Hill v Harpurhey Wesleyans | 18950817 | match information |
| 53 | Manchester v Cheadle Hulme | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Worcestershire v Cheshire | 18950819 | match information |
| 56 | Bollington Fairfield v Bollington | 18950824 | match information |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | 18950824 | match information |
| 57 | Phoenix v Cornbrook | 18950824 | match information |
| 59 | Formby v New Brighton | 18950907 | match information |
| 59 | Wallasey v Oxton 2nd XI | 18950907 | match information |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 54 | Birkenhead Victoria v New Brighton | Victoria v New Brighton | 0.807 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Mr Wynne's Team v Mr Griffith's Team | 0.812 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 54 | Bromborough Pool v Birkenhead Police | Bromborough Pool v Police | 0.82 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Lavenhulme Second XI | 0.822 |
| 57 | Seymour Mead's v Stockport Post Office | Six Works Men's v Stockport Post Office | 0.827 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 27 | Biscuit Factory player statistics | Biscuit Factory Cricket Club player statistics | 0.835 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Brethoven | 0.836 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 49 | Mr G H Ling's XI v Cheadle | Mr GH Lloyd's XI v Cheadle | 0.84 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Chadle Hulme v Sale Second XI | 0.841 |
| 51 | Cheadle v Heaton Mersey | Kersal v Heaton Mersey | 0.844 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill BS v Harpurhey Wesleyans | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 41 | Histon and Impington v A Team of the Old Higher Grade | Histon And Impington v Old Higher Grade | 0.848 |
| 26 | Bradfield v A. Sutton's XI | Milfield v A Sutton's XI | 0.851 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 58 | Liverpool player statistics | Liverpool First XI player statistics | 0.857 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 51 | Phoenix v Manchester | Phoenix v Masters | 0.865 |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | Liverpool v Rock Ferry Second XI | 0.865 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 27 | Royal Berks Seed Establishment player statistics | Royal Berks Seed Establishment Cricket Club player statistics | 0.881 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 46 | Langley v Leek Highfield | Langley v Lane End Highfield | 0.885 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory B XI v Clayston's Athletic Loxdon | 0.886 |
| 2 | F. Gentle's XI v Waterlow's | Mr F Gentle's XI v Waterlow's OC | 0.889 |
| 33 | Berkley's XI v Greaves' XI | Mr Berkley's XI v Mr Greaves' XI | 0.889 |
| 34 | Taplow Station v Bryanston Square | Taplow Station v Baylston-Square | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads Club First XI | 0.893 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second XI v Longsight Second XI | 0.911 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 37 | Quarterman's Firm v R Ford's Firm | Mr Quarterman's Firm v Mr R Ford's Firm | 0.912 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Third XI v South Manchester Second XI | 0.913 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill SS v Haughton Wesleyans First | 0.913 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 33 | Rayners XI v Permanent Staff of the 3rd Batt. Oxford Light Infantry | Bayners XI v Permanent Staff Of The Second Batt Oxford Light Infantry | 0.92 |
| 2 | Waterlow's v Aylesbury Printing Works | Waterlow's OC v Aylesbury Printing Works' OC | 0.923 |
| 4 | Mr. Haviland's XI v Luton Villa Road | Mr Haviland's XI v Luton Villa-Road CO | 0.93 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 59 | Birkenhead Park A player statistics | Birkenhead Park A team player statistics | 0.933 |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | Wycombe Bells v Wanderers V Holloway's Boot Operatives OC | 0.937 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 20 | Newbury v C.E. Keyser's XI | Newbury v Mr CE Keyser's XI | 0.939 |
| 57 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v RP Hammond's Team | 0.939 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | Mr TW Girdlestone's XI v Girdlestones (charterhouse) | 0.941 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 59 | YMCA v Ravenscroft | YMCA v Raverscroft | 0.944 |
| 52 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Reddish v St Thomas' Hyde | 0.946 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane Addington | 0.946 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 33 | High Wycombe v E. Stevens' XI | High Wycombe v Mr E Stevens' XI | 0.947 |
| 38 | Marlow v J Monro Walker's XI | Marlow v Mr J Monro Walker's XI | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |
| 49 | St Matthew's v Hanover 2nd XI | St Matthew's v Hanover Second | 0.949 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton Married v Single | 18950805 | match information |
| 4 | Waterlows' v St Matthew's Luton | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of Third Volunteer Battalion | 18950807 | match information |
| 11 | Town Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' OC v Boys' Brigade (second Wokingham Company) Second XI | 18950518 | match information |
| 15 | Earley St Peter's fixture update | 18950525 | fixture information |
| 16 | Reading School First XI player statistics | 18950715 | statistics |
| 16 | Reading School Second XI player statistics | 18950715 | statistics |
| 18 | Reading Cricket Week | 18950810 | newspaper cuttings |
| 24 | Abingdon Cricket and Football Club | 18950000 | team information |
| 24 | Abingdon Cricket and Football Club Second XI | 18950000 | team information |
| 24 | Abingdon Cricket and Football Club Second XI player statistics | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club player statistics | 18950000 | statistics |
| 26 | A Sutton's XI v Unknown |  | match information |
| 26 | Buckingham v Newtown |  | match information |
| 26 | Newtown match list |  | team information |
| 29 | Lechlade Cricket Club annual dinner | 18951031 | team information |
| 32 | Wycombe | 18950719 | newspaper cuttings |
| 33 | Saturday's Fixtures | 18950809 | fixture information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 34 | Wycombe Marsh PL | 18950730 | organisation information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford St Martin | 18950803 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 39 | Four Veterans v Four Juniors (single Wicket) | 18950826 | match information |
| 40 | Old Higher Grade v Sawston | 18950727 | match information |
| 41 | Sport and Play Gossip | 18950803 | newspaper cuttings |
| 42 | New Museums Professors And Demonstrators v Assistants | 18950810 | match information |
| 43 | County v Borough Police | 18950807 | match information |
| 43 | KS Ranjitsinhji | 18950810 | biography |
| 43 | Leading batsmen player statistics | 18950803 | statistics |
| 43 | Sport and Play | 18950810 | newspaper cuttings |
| 48 | Garston v Liverpool Second XI | 18950708 | match information |
| 50 | Bollington v Heaton Mersey | 18950800 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950800 | match information |
| 50 | Castleton v Stockport | 18950727 | match information |
| 50 | GH Ling's XI v Cheshire | 18950800 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First XI | 18950800 | match information |
| 50 | Macclesfield v Poynton | 18950800 | match information |
| 50 | North East Cheshire League | 18950000 | league information |
| 50 | Phoenix v Manchester South End | 18950800 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950800 | match information |
| 50 | Saturday's Matches | 18950727 | newspaper cuttings |
| 50 | St Matthew's v Hanover Second XI | 18950800 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's Final Tie | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Stockport and District Shield Competition | 18950000 | league information |
| 50 | Urmston v Bramall | 18950800 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950800 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950800 | match information |
| 51 | St Joseph's v St Thomas' | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950800 | match information |
| 52 | Bollington Second XI v Bosworth | 18950800 | match information |
| 52 | Phoenix v Martinrigg | 18950800 | match information |
| 52 | Stockport v Great Moor | 18950800 | match information |
| 53 | Harpurhey BS v Haslingden Wesleyans Second XI | 18950817 | match information |
| 53 | Manchester v Cheshire Rolling | 18950817 | match information |
| 54 | Birkenhead Advertiser cricket notes | 18950824 | newspaper cuttings |
| 54 | Cheshire v Worcestershire | 18950800 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Woodland season summary | 18950000 | team information |
| 55 | St John's Second XI v Bebington Bible Class | 18950821 | match information |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 57 | Cheetham v Levenshulme Second Elevens | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950000 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 58 | Liverpool An Eleven player statistics | 18950000 | statistics |
| 58 | Liverpool Second XI player statistics | 18950000 | statistics |
| 58 | Liverpool team aggregates | 18950000 | statistics |
| 59 | Fixture list for 14 September 1895 | 18950914 | fixture information |
| 59 | New Brighton v Formby | 18950907 | match information |
| 59 | Oxton Second XI v Wallasey | 18950000 | match information |
| 59 | Rock Ferry Second XI brief statistics | 18950000 | statistics |
| 61 | Birkenhead Park player statistics | 18950914 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950914 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Cricket Notes | 18950914 | newspaper cuttings |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950914 | statistics |
| 61 | Rock Ferry player statistics | 18950914 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
