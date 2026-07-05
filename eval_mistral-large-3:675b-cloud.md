# Evaluation: mistral-large-3:675b-cloud vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 343/388 (88.4%)**
- Exact-key matches: 235; fuzzy-only matches: 108
- Date agreement (matched pairs, both dated): 248/343 (72.3%)
- Content-type agreement (type-blind matches): 340/342 (99.4%)
- Missed Willis rows: 45
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 136

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 308 | 350 | 88.0% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 28 | 30 | 93.3% |
| team information | 3 | 4 | 75.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | 18950727 | match information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Biscuit Factory team aggregates | 18950000 | statistics |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 37 | Stokenchurch v Skirmett | 18950806 | match information |
| 39 | W Pearce's (Wycombe) XI v Southall | 18950824 | match information |
| 40 | Sawston v Old Higher Grade | 18950727 | match information |
| 40 | Sutton v Haddenham | 18950727 | match information |
| 42 | Assistants v Professors and Demonstrators | 18950810 | match information |
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
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 54 | Liverpool v New Brighton | 18950821 | match information |
| 54 | Worcestershire v Cheshire | 18950819 | match information |
| 56 | Bollington Fairfield v Bollington | 18950824 | match information |
| 57 | Phoenix v Cornbrook | 18950824 | match information |
| 59 | Formby v New Brighton | 18950907 | match information |
| 61 | Bebington Bible Class CC v Magazines | 18950907 | match information |
| 61 | Birkenhead St John's v Cedar | 18950907 | match information |
| 61 | Gardeners v Coachmen | 18950911 | match information |
| 61 | Rock Ferry 2nd XI v Cheadle Hulme 2nd XI | 18950907 | match information |
| 61 | Spital v Bromborough Pool | 18950907 | match information |
| 61 | Tranmere Wesley v West Derby 2nd XI | 18950907 | match information |
| 61 | Wallasey v Oxton 2nd XI | 18950907 | match information |
| 61 | YMCA v Ravenscroft | 18950907 | match information |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 26 | Bradfield v A. Sutton's XI | Milfield v Mr A Sutton's XI | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 54 | Birkenhead Victoria v New Brighton | Victoria v New Brighton | 0.807 |
| 26 | Stockcross v Chieveley | Stockcross v Chilterny | 0.818 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Lavenhulme Second XI | 0.822 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Brethoven | 0.836 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 57 | Seymour Mead's v Stockport Post Office | Sixworks Men's v Stockport Post Office | 0.838 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Chadle Hulme v Sale Second XI | 0.841 |
| 51 | Cheadle v Heaton Mersey | Kersal v Heaton Mersey | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable v Aston Clinton | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservatives | 0.847 |
| 41 | Histon and Impington v A Team of the Old Higher Grade | Histon And Impington v Old Higher Grade | 0.848 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire Hill B S v Harpurhey Wesleyans | 0.857 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 49 | Mr G H Ling's XI v Cheadle | Mr G H Lloyd's XI v Cheadle | 0.863 |
| 51 | Phoenix v Manchester | Phoenix v Masters | 0.865 |
| 33 | Berkley's XI v Greaves' XI | Mr Berkley XI v Mr Greaves XI | 0.868 |
| 57 | Reddish St Joseph's v Hyde St Thomas' | St Joseph's v Hyde St Thomas' | 0.871 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 18 | Reading v C.E. Keyser's XI | Reading v Mr C E Keymer's XI | 0.88 |
| 60 | Birkenhead Park "A" Team player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Clayston's Athletic | 0.884 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 46 | Langley v Leek Highfield | Langley v Lane End Highfield | 0.885 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park Second XI player statistics | 0.894 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 20 | Avondale v Oxford-Road | Ayondale v Oxford Road | 0.909 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | Mr T W Girdlestone's XI v Girdlestones Charterhouse | 0.911 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second XI v Longsight Second XI | 0.911 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 37 | Quarterman's Firm v R Ford's Firm | Mr Quarterman's Firm v Mr R Ford's Firm | 0.912 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Third XI v South Manchester Second XI | 0.913 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire Hill Second XI v Stockport Lads Club First XI | 0.913 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 20 | Newbury v C.E. Keyser's XI | Newbury v Mr C E Keyser's XI | 0.92 |
| 33 | Rayners XI v Permanent Staff of the 3rd Batt. Oxford Light Infantry | Bayners XI v Permanent Staff Of The Second Batt Oxford Light Infantry | 0.92 |
| 34 | Taplow Station v Bryanston Square | Taplow Station v Baylston Square | 0.923 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 33 | J. Grenfell's XI v Beaconsfield | Mr J Grenfell XI v Beaconsfield | 0.933 |
| 59 | Birkenhead Park A player statistics | Birkenhead Park A Team player statistics | 0.933 |
| 56 | Didsbury 2nd XI v Poynton 2nd XI | Dunesbury Second XI v Poynton Second XI | 0.935 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 2 | F. Gentle's XI v Waterlow's | Mr F Gentle's XI v Waterlow's | 0.941 |
| 34 | Wycombe Y.M.C.A. v A. Gray's XI | Wycombe YMCA v Mr A Gray's XI | 0.943 |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | Wycombe Bells Wanderers v Holloway's Boot Operatives | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 59 | YMCA v Ravenscroft | YMCA v Raverscroft | 0.944 |
| 52 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Reddish v St Thomas' Hyde | 0.946 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane Addington | 0.946 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |
| 20 | London-Street Institute v Co-Operative | London Street Institute v Co Operative | 0.947 |
| 20 | Gentlemen of Berkshire v C.D. Rose's XI | Gentlemen Of Berkshire v Mr C D Rose's XI | 0.947 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 33 | High Wycombe v E. Stevens' XI | High Wycombe v Mr E Stevens XI | 0.947 |
| 38 | Marlow v J Monro Walker's XI | Marlow v Mr J Monro Walker's XI | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill SS v Haughton Wesleyans First XI | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton Married v Houghton Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's Luton | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of Third Volunteer Battalion | 18950807 | match information |
| 11 | Dunstable Volunteers players | 18950824 | player information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' OC v Boys' Brigade Second XI | 18950518 | match information |
| 15 | Earley St Peter's | 18950525 | fixture information |
| 16 | A T Cliff | 18950000 | biography |
| 16 | E E Todd | 18950000 | biography |
| 16 | F G Clarke | 18950000 | biography |
| 16 | F W Parfitt | 18950000 | biography |
| 16 | H A Turner | 18950000 | biography |
| 16 | J Hodge | 18950000 | biography |
| 16 | P L Mousley | 18950000 | biography |
| 16 | R H Jackson | 18950000 | biography |
| 16 | R H Morris | 18950000 | biography |
| 16 | R H Mousley | 18950000 | biography |
| 16 | Reading School First XI player statistics | 18950715 | statistics |
| 16 | Reading School Second XI player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 16 | W Hatt | 18950000 | biography |
| 17 | Biscuit Factory Second XI v White Cross | 18950727 | match information |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Reading match list | 18950800 | team information |
| 18 | Reading v Godalming | 18950810 | match information |
| 18 | Reading v Hounslow Garrison | 18950809 | match information |
| 18 | Sunningdale School team aggregates | 18950000 | statistics |
| 19 | Mr T W Girdlestone's XI team aggregates | 18950000 | statistics |
| 19 | Sunningdale School season information | 18950000 | season information |
| 24 | Abingdon Second XI match list | 18950000 | team information |
| 24 | Abingdon Second XI player statistics | 18950000 | statistics |
| 24 | Abingdon match list | 18950000 | team information |
| 25 | Newbury 1895 season summary | 18950000 | team information |
| 26 | Buckingham v Newtown | 18950900 | match information |
| 26 | Mr A Sutton's XI v Unknown | 18950900 | match information |
| 26 | Newtown match list | 18950000 | team information |
| 27 | 49th Regimental District team aggregates | 18950900 | team information |
| 27 | Biscuit Factory team aggregates | 18950000 | team information |
| 27 | Royal Berks Seed Establishment team information | 18950900 | team information |
| 29 | Lechlade annual dinner | 18951101 | organisation information |
| 29 | Lechlade team aggregates | 18950000 | statistics |
| 30 | Maidenhead team aggregates | 18951100 | statistics |
| 32 | Bastick Cup Competition final arrangements | 18950727 | fixture information |
| 32 | Church Room v Wheeler End Blue Star | 18950720 | fixture information |
| 32 | St John's match list | 18950800 | team information |
| 32 | St John's v West End United | 18950720 | fixture information |
| 32 | Wycombe Grammar School Past and Present v Wycombe | 18950718 | fixture information |
| 32 | Wycombe Reserves v Borlase School | 18950720 | fixture information |
| 32 | Wycombe YMCA v Newland Bible Class | 18950720 | fixture information |
| 33 | Saturday fixtures | 18950803 | fixture information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 34 | Wycombe Marsh match list | 18950000 | team information |
| 34 | Wycombe YMCA fixture information | 18950800 | fixture information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford St Martin | 18950803 | match information |
| 36 | Cippenham v Carlton | 18950805 | match information |
| 37 | Bucks Rural League | 18950800 | league information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 39 | Mr W Pearce's XI v Southall | 18950824 | match information |
| 40 | Mr Hoare's Sutton XI v Haddenham | 18950727 | match information |
| 40 | Old Higher Grade v Sawston | 18950727 | match information |
| 41 | Cambridge County v Hunts | 18950731 | match information |
| 41 | Cambridge County v MCC And Ground | 18950731 | match information |
| 41 | Cambridgeshire Cricket Cup final fixture | 18950800 | fixture information |
| 41 | Old Higher Grade v Sawston | 18950727 | match information |
| 42 | New Museums Professors And Demonstrators v Assistants | 18950810 | match information |
| 43 | First-class batsmen averages | 18950800 | statistics |
| 43 | Kumar Shri Ranjitsinhji | 18950000 | biography |
| 48 | Garston v Liverpool Second XI | 18950706 | match information |
| 49 | North East Cheshire League | 18950800 | league information |
| 49 | Stockport and District Shield Competition | 18950800 | award information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | Castleton v Stockport | 18950727 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First XI | 18950727 | match information |
| 50 | Macclesfield v Poynton | 18950727 | match information |
| 50 | Mr G H Ling's XI v Cheshire | 18950727 | match information |
| 50 | North East Cheshire League | 18950800 | league information |
| 50 | Phoenix v Manchester South End | 18950727 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950727 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950727 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Raddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Stockport and District Shield Competition | 18950800 | league information |
| 50 | Urmston v Bramall | 18950727 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950814 | match information |
| 51 | Hanover First XI v Heywood's Excelsior First XI | 18950800 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950809 | match information |
| 51 | St Joseph's Handen v St Thomas' Hyde | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950800 | match information |
| 52 | Bollington Second XI v Bosworth | 18950816 | match information |
| 52 | Phoenix v Martinrigg | 18950816 | match information |
| 52 | Stockport v Great Moor | 18950816 | match information |
| 53 | Harpurhey B S v Haslingden Wesleyans Second XI | 18950800 | match information |
| 53 | Manchester v Cheshire Rolling | 18950800 | match information |
| 54 | Bromhro Pool v Police First XI | 18950817 | match information |
| 54 | Cheshire v Worcester | 18950800 | match information |
| 54 | New Brighton v Liverpool | 18950821 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Wirral | 18950817 | newspaper cuttings |
| 54 | Woodland season summary | 18950000 | team information |
| 55 | All Saints open dates | 18950800 | fixture information |
| 55 | All Saints v Comet | 18950824 | match information |
| 55 | St John's Second XI v Bebington Bible Class | 18950817 | match information |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 56 | St Thomas' Athletic match list | 18950800 | team information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Phoenix Second XI v Mossley Second XI | 18950824 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 57 | St Joseph's team information | 18950800 | team information |
| 57 | St Thomas' Athletic fixture information | 18950831 | fixture information |
| 58 | Birkenhead Victoria team information | 18950000 | team information |
| 58 | Formby team information | 18950000 | team information |
| 58 | Liverpool team information | 18950000 | team information |
| 58 | Northern team information | 18950000 | team information |
| 58 | Presco team information | 18950000 | team information |
| 59 | Birkenhead Park team aggregates | 18950900 | statistics |
| 59 | Birkenhead Victoria First XI team aggregates | 18950900 | statistics |
| 59 | Birkenhead fixture information | 18950914 | fixture information |
| 59 | New Brighton v Formby | 18950907 | match information |
| 59 | Oxton team aggregates | 18950900 | statistics |
| 59 | Rock Ferry Second XI player statistics | 18950900 | statistics |
| 59 | Rock Ferry Second XI team aggregates | 18950900 | statistics |
| 59 | Rock Ferry team aggregates | 18950900 | statistics |
| 59 | St Aidan's team information | 18950900 | team information |
| 60 | Birkenhead Park team aggregates | 18950900 | statistics |
| 60 | Birkenhead Victoria team aggregates | 18950900 | statistics |
| 60 | Oxton Second XI team aggregates | 18950900 | statistics |
| 60 | Oxton match list | 18950900 | team information |
| 60 | Rock Ferry Second XI team aggregates | 18950900 | statistics |
| 60 | Rock Ferry team aggregates | 18950900 | statistics |
