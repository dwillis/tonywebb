# Evaluation: kimi-k2.6 vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 336/388 (86.6%)**
- Exact-key matches: 243; fuzzy-only matches: 93
- Date agreement (matched pairs, both dated): 261/336 (77.7%)
- Content-type agreement (type-blind matches): 342/342 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 294/336 (87.5%)
- Missed Willis rows: 52
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 106

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 304 | 350 | 86.9% |
| newspaper cuttings | 1 | 2 | 50.0% |
| player information | 0 | 1 | 0.0% |
| statistics | 27 | 30 | 90.0% |
| team information | 3 | 4 | 75.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 16 | Reading School match list | 18950802 | team information |
| 16 | Reading School players | 18950802 | player information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 18 | Reading v W. Howard Palmer's XI | 18950807 | match information |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | 18950731 | match information |
| 20 | Gentlemen of Berkshire v C.D. Rose's XI | 18950816 | match information |
| 24 | Abingdon player statistics | 18950000 | statistics |
| 26 | Bradfield v A. Sutton's XI | 18950907 | match information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Biscuit Factory team aggregates | 18950000 | statistics |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 33 | High Wycombe v E. Stevens' XI | 18950803 | match information |
| 33 | Rayners XI v Permanent Staff of the 3rd Batt. Oxford Light Infantry | 18950805 | match information |
| 34 | Taplow Station v Bryanston Square | 18950803 | match information |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 37 | Pine Apple v King's Head | 18950805 | match information |
| 37 | Stokenchurch v Skirmett | 18950806 | match information |
| 38 | Marlow v J Monro Walker's XI | 18950824 | match information |
| 39 | W Pearce's (Wycombe) XI v Southall | 18950824 | match information |
| 41 | Cambridge | 18950803 | newspaper cuttings |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 43 | County of Cambridge Police v Borough Police | 18950803 | match information |
| 46 | Langley v Leek Highfield | 18950615 | match information |
| 48 | Garston v Liverpool 3rd | 18950700 | match information |
| 49 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Cheadle v Heaton Mersey | 18950810 | match information |
| 51 | Hazel Grove UC v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Macclesfield v Levenshulme | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 51 | St Joseph's (Reddish) v St Thomas' (Hyde) | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 53 | Lancashire Hill v Harpurhey Wesleyans | 18950817 | match information |
| 53 | Manchester v Cheadle Hulme | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 55 | Helsby v Port Sunlight | 18950817 | match information |
| 56 | Bollington Fairfield v Bollington | 18950824 | match information |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | 18950824 | match information |
| 57 | Phoenix v Cornbrook | 18950824 | match information |
| 57 | Stockport 2nd XI v Cheadle Hulme 2nd XI | 18950824 | match information |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 39 | Four Veterans v Four Juniors | Four Veterans v Four Juniors Single Wicket | 0.8 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 52 | Sale v Cheadle Hulme | Sale v Chadkirk Hulme | 0.829 |
| 14 | All Saints' v Boys' Brigade | All Saints' OC v Boys' Brigade Second XI | 0.833 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir, Bourne End v Little Marlow | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill B S v Harpurhey Wesleyans | 0.835 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 57 | Seymour Mead's v Stockport Post Office | Sixworks Men's v Stockport Post Office | 0.838 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town v Aston Clinton | 0.844 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Third v South Manchester Second | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second v Longsight Second | 0.849 |
| 57 | Langley v Bollington | Langley v Bollington Second | 0.851 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall v Stockport Second XI | 0.853 |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | Liverpool v Rock Ferry Second Xis | 0.853 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 49 | Mr G H Ling's XI v Cheadle | Mr G H Lloyd's XI v Cheadle | 0.863 |
| 51 | Phoenix v Manchester | Phoenix v Masters | 0.865 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 59 | Birkenhead Park A player statistics | Birkenhead Park Park A Team player statistics | 0.875 |
| 34 | Colman Green v Gerrards Cross | Cotham Green v Gerards Cross | 0.877 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 4 | Mr. Haviland's XI v Luton Villa Road | Mr R H Haviland's XI v Luton Villa-Road CO | 0.88 |
| 18 | Reading v C.E. Keyser's XI | Reading v Mr C E Keymer's XI | 0.88 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 26 | Stockcross v Chieveley | Stockcross v Chilterley | 0.889 |
| 33 | Berkley's XI v Greaves' XI | Mr Berkley's XI v Mr Greaves' XI | 0.889 |
| 54 | Worcestershire v Cheshire | Cheshire v Worcester | 0.889 |
| 37 | Long Crendon v Dinton | Long Crendon v Biston | 0.905 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 37 | Quarterman's Firm v R Ford's Firm | Mr Quarterman's Firm v Mr R Ford's Firm | 0.912 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire Hill Second XI v Stockport Lads' Club First XI | 0.913 |
| 57 | Didsbury 2nd XI v Poynton 2nd XI | Didsbury Second v Poynton Second | 0.914 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 20 | Newbury v C.E. Keyser's XI | Newbury v Mr C E Keyser's XI | 0.92 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 26 | Speen player statistics | Speen C.C player statistics | 0.939 |
| 2 | F. Gentle's XI v Waterlow's | Mr F Gentle's XI v Waterlow's | 0.941 |
| 21 | Burghclere v Adbury House | Burghclere v Ashbury House | 0.941 |
| 34 | Wycombe Y.M.C.A. v A. Gray's XI | Wycombe YMCA v Mr A Gray's XI | 0.943 |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | Wycombe Bells Wanderers v Holloway's Boot Operatives | 0.943 |
| 57 | Reddish St Joseph's v Hyde St Thomas' | Maddish St Joseph's v Hyde St Thomas' | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 59 | YMCA v Ravenscroft | YMCA v Raverscroft | 0.944 |
| 52 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Reddish v St Thomas' Hyde | 0.946 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane Addington | 0.946 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 26 | Shepherd's XI v Woolley Park | Up Shepherd's XI v Woolley Park | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill SS v Haughton Wesleyans First XI | 0.947 |
| 50 | Reddish St Joseph's v Union Street Hyde | Raddish St Joseph's v Union-Street Hyde | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton Married v Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's Luton | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of Third Volunteer Battalion | 18950807 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 16 | Reading School Cricket Club match list and statistics | 18950800 | team information |
| 16 | Reading School Cricket Club player statistics | 18950800 | statistics |
| 16 | Reading School Cricket Club players | 18950800 | player information |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Reading v Mr W Howard Palmer's XI | 18950807 | match information |
| 19 | T W Girdlestone's XI v Girdlestones | 18950731 | match information |
| 20 | Gentlemen Of Berkshire v Mr C D Rose's XI | 18950816 | match information |
| 24 | Abingdon Cricket and Football Club | 18950000 | team information |
| 24 | Abingdon Cricket and Football Club Second XI player statistics | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club player statistics | 18950000 | statistics |
| 26 | Buckingham v Newtown | 18950000 | match information |
| 26 | Milfield v Mr A Sutton's XI | 18950907 | match information |
| 26 | Newtown team information | 18950000 | team information |
| 27 | 49th Regimental District team information | 18950920 | team information |
| 27 | Biscuit Factory team information | 18950920 | team information |
| 27 | Royal Berks Seed Establishment team information | 18950920 | team information |
| 29 | Lechlade Cricket Club dinner | 18951031 | newspaper cuttings |
| 29 | Lechlade match list | 18950000 | team information |
| 30 | Maidenhead match list | 18951113 | team information |
| 32 | Church Room | 18950719 | newspaper cuttings |
| 32 | St John's | 18950719 | newspaper cuttings |
| 32 | Wycombe | 18950719 | newspaper cuttings |
| 33 | Bayners XI v Permanent Staff Of The Second Batt. Oxford Light Infantry | 18950805 | match information |
| 33 | High Wycombe v Mr E Stevens XI | 18950803 | match information |
| 33 | Saturday's Fixtures | 18950803 | fixture information |
| 34 | Gerards Cross v Osborne Stevens And Co | 18950802 | match information |
| 34 | South Bucks Free Press: Friday 9 August 1895 | 18950809 | match information |
| 34 | Taplow Station v Post Office Telegraphs London | 18950805 | match information |
| 34 | Wycombe YMCA match list | 18950000 | team information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford St Martin | 18950803 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 37 | Bucks Rural League | 18950000 | league information |
| 37 | Fine Apple v King's Head | 18950805 | match information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 38 | Marlow v Mr J Monro Walker's XI | 18950824 | match information |
| 39 | Mr W Pearce's Wycombe XI v Southall | 18950824 | match information |
| 41 | Cambridge County Cricket Club team information | 18950800 | team information |
| 41 | Cambridgeshire Cricket Cup Competition final fixture information | 18950800 | fixture information |
| 41 | Cambridgeshire Cricket Cup Competition final team information | 18950800 | team information |
| 41 | Cassandra Club team information | 18950800 | team information |
| 41 | Histon And Impington v Old Higher Grade | 18950800 | match information |
| 41 | Sawston v Old Higher Grade | 18950727 | match information |
| 43 | Cambs Cricket Association Cup final preview | 18950800 | newspaper cuttings |
| 43 | County v Borough Police | 18950807 | match information |
| 43 | K S Ranjitsinhji | 18950800 | biography |
| 43 | Leading dozen batsmen averages | 18950800 | statistics |
| 46 | Langley v Lane End | 18950615 | match information |
| 48 | Garston v Liverpool Second XI | 18950000 | match information |
| 49 | Hollington v Heaton Mersey | 18950727 | match information |
| 50 | Bollington v Heaton Mersey | 18950800 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950800 | match information |
| 50 | Castleton v Stockport | 18950800 | match information |
| 50 | G H Ling's XI v Cheshire | 18950800 | match information |
| 50 | Lancashire Hill S S v Haughton Wesleyans First XI | 18950800 | match information |
| 50 | Macclesfield v Poynton | 18950800 | match information |
| 50 | Phoenix v Manchester South End | 18950800 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950800 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950800 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950800 | match information |
| 50 | Stockport Congregational v Raddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950800 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950816 | match information |
| 51 | Hanover v Heywood's Excelsior | 18950810 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950816 | match information |
| 51 | Kersal v Heaton Mersey | 18950816 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950816 | match information |
| 51 | St Joseph's Handen v St Thomas' Hyde | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950816 | match information |
| 52 | Bollington Second XI v Bosworth | 18950809 | match information |
| 52 | Chadkirk Hulme v Sale Second XI | 18950809 | match information |
| 52 | Phoenix v Martinrigg | 18950809 | match information |
| 52 | Poynton v Great Moor | 18950809 | match information |
| 53 | Harpurhey B S v Haslingden Wesleyans Second Team | 18950817 | match information |
| 53 | Manchester v Cheshire Rolling | 18950817 | match information |
| 54 | Bromboro Pool v Police First XI | 18950817 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team statistics | 18950000 | statistics |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 57 | Cheetham v Levenshulme Second Elevens | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950824 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 57 | Stockport And Cheadle Hulme Second | 18950824 | match information |
| 59 | Birkenhead fixture information | 18950914 | fixture information |
| 59 | Rock Ferry Second XI player statistics | 18950914 | statistics |
| 60 | Birkenhead Victoria First XI team aggregates | 18950914 | statistics |
| 60 | Oxton team information | 18950914 | team information |
| 60 | Rock Ferry Second XI team aggregates | 18950914 | statistics |
| 61 | Birkenhead Park player statistics | 18950000 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950000 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950000 | statistics |
| 61 | Rock Ferry player statistics | 18950000 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
