# Evaluation: qwen3.5_397b-cloud_fixed vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 345/388 (88.9%)**
- Exact-key matches: 240; fuzzy-only matches: 105
- Date agreement (matched pairs, both dated): 228/342 (66.7%)
- Content-type agreement (type-blind matches): 345/345 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 304/345 (88.1%)
- Missed Willis rows: 43
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 95

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 313 | 350 | 89.4% |
| newspaper cuttings | 1 | 2 | 50.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 26 | 30 | 86.7% |
| team information | 3 | 4 | 75.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 24 | Abingdon player statistics | 18950000 | statistics |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Biscuit Factory team aggregates | 18950000 | statistics |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 33 | Rayners XI v Permanent Staff of the 3rd Batt. Oxford Light Infantry | 18950805 | match information |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 37 | Pine Apple v King's Head | 18950805 | match information |
| 37 | Stokenchurch v Skirmett | 18950806 | match information |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | 18950824 | match information |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 43 | Cambridge | 18950810 | newspaper cuttings |
| 43 | County of Cambridge Police v Borough Police | 18950803 | match information |
| 46 | Langley v Leek Highfield | 18950615 | match information |
| 48 | Garston v Liverpool 3rd | 18950700 | match information |
| 49 | Bollington v Heaton Mersey | 18950727 | match information |
| 49 | Castleton v Stockport | 18950727 | match information |
| 49 | Mr G H Ling's XI v Cheadle | 18950727 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Cheadle v Heaton Mersey | 18950810 | match information |
| 51 | Hazel Grove UC v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Macclesfield v Levenshulme | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 53 | Lancashire Hill v Harpurhey Wesleyans | 18950817 | match information |
| 53 | Manchester v Cheadle Hulme | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 56 | Bollington Fairfield v Bollington | 18950824 | match information |
| 57 | Phoenix v Cornbrook | 18950824 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 29 | Lechlade player statistics | Lechlade Cricket Club player statistics | 0.8 |
| 52 | Kersal v Heaton Mersey | Kersal v Hanover Mersey | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington 2nd XI | 0.8 |
| 58 | Liverpool player statistics | Liverpool Cricket Club player statistics | 0.806 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Lavenhulme Second XI | 0.822 |
| 51 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Handen v St Thomas' (Hyde) | 0.827 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 14 | All Saints' v Boys' Brigade | All Saints' v Boys' Brigade Second XI | 0.833 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton 2nd XI | 0.833 |
| 27 | Biscuit Factory player statistics | Biscuit Factory Cricket Club player statistics | 0.835 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Brethoven | 0.836 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 57 | Seymour Mead's v Stockport Post Office | Sixworks Men's v Stockport Post Office | 0.838 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Chadle Hulme v Sale 2nd XI | 0.841 |
| 51 | Phoenix v Manchester | Phoenix v Marsters | 0.842 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill BS v Harpurhey Wesleyans | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 26 | Bradfield v A. Sutton's XI | Milfield v A Sutton's XI | 0.851 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 56 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 57 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | Liverpool v Rock Ferry 2nd XI | 0.865 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 27 | Royal Berks Seed Establishment player statistics | Royal Berks Seed Establishment Cricket Club player statistics | 0.881 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall 1st XI v Stockport 2nd XI | 0.883 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 60 | Oxton Second XI player statistics | Oxton Second Eleven player statistics | 0.886 |
| 4 | Mr. Haviland's XI v Luton Villa Road | R H Haviland's XI v Luton Villa-Road CO | 0.889 |
| 26 | Stockcross v Chieveley | Stockcross v Chilterley | 0.889 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Wynne's XI v Griffith's XI | 0.889 |
| 34 | Taplow Station v Bryanston Square | Taplow Station v Baylston-Square | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 44 | New Chesterton Juniors v Liberal 2nd XI | New Chesterton Juniors Second XI v Liberal 2nd XI | 0.894 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry First Eleven player statistics | 0.897 |
| 60 | Rock Ferry Second XI player statistics | Rock Ferry Second Eleven player statistics | 0.9 |
| 37 | Long Crendon v Dinton | Long Crendon v Biston | 0.905 |
| 18 | Reading v W. Howard Palmer's XI | W H Palmer's XI v Reading | 0.906 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservatives Club | 0.911 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second XI v Longsight Second XI | 0.911 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Third XI v South Manchester 2nd XI | 0.913 |
| 59 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria First Eleven player statistics | 0.917 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria First Eleven player statistics | 0.917 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 18 | Reading v C.E. Keyser's XI | Reading v C E Keymer's XI | 0.936 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill S S v Haughton Wesleyans 1st XI | 0.938 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | T W Girdlestone's XI v Girdlestones Charterhouse | 0.939 |
| 21 | Burghclere v Adbury House | Burghclere v Ashbury House | 0.941 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 54 | St Mary's v Tranmere Wesley | St Mary's v Tranmere Wesleyans | 0.945 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane Addington | 0.946 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |
| 50 | Reddish St Joseph's v Union Street Hyde | Raddish St Joseph's v Union-Street Hyde | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton CC Married v Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Third Volunteer Battalion Remainder | 18950807 | match information |
| 11 | Town Second XI v Carter | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950524 | match information |
| 15 | Earley | 18950525 | newspaper cuttings |
| 16 | Reading School First XI player statistics | 18950715 | statistics |
| 16 | Reading School Second XI player statistics | 18950715 | statistics |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Sunningdale School team aggregates | 18950000 | statistics |
| 19 | Mr T W Girdlestone's XI team aggregates | 18950800 | statistics |
| 24 | Abingdon Cricket and Football Club | 18950000 | team information |
| 24 | Abingdon Cricket and Football Club Second XI | 18950000 | team information |
| 24 | Abingdon Cricket and Football Club Second XI player statistics | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club player statistics | 18950000 | statistics |
| 26 | Buckingham v Newtown |  | match information |
| 26 | Newtown match list | 18950912 | team information |
| 27 | 49th Regimental District CC team aggregates | 18950000 | statistics |
| 27 | Biscuit Factory | 18950000 | team information |
| 27 | Royal Berks Seed Establishment | 18950000 | team information |
| 29 | Lechlade | 18951031 | team information |
| 30 | Maidenhead match list | 18950000 | team information |
| 32 | Church Room | 18950000 | newspaper cuttings |
| 32 | St. John's | 18950000 | newspaper cuttings |
| 32 | Wycombe Y.M.C.A. | 18950000 | newspaper cuttings |
| 33 | Bayners XI v Permanent Staff Of The Second Batt Oxford Light Infantry | 18950805 | match information |
| 33 | Saturday's fixtures | 18950810 | fixture information |
| 34 | Gerrards Cross v Osborne Stevens And Co | 18950731 | match information |
| 34 | Wycombe Marsh PL | 18950730 | organisation information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford S Martin | 18950803 | match information |
| 36 | Cippenham v Carlton | 18950805 | match information |
| 37 | Fine Apple v King's Head | 18950805 | match information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 38 | Wycombe Bells v Wanderers V Holloway Boot Operatives OC | 18950824 | match information |
| 41 | Histon and Impington v Old Higher Grade | 18950727 | match information |
| 43 | Cambridge Express | 18950810 | newspaper cuttings |
| 43 | County v Borough Police | 18950807 | match information |
| 43 | K S Ranjitsinhji | 18950810 | biography |
| 46 | Langley v Lane End | 18950615 | match information |
| 48 | Garston v Liverpool 2nd XI | 18950705 | match information |
| 49 | G H Lloyd's XI v Cheadle | 18950727 | match information |
| 49 | Hollington v Heaton Mersey | 18950727 | match information |
| 50 | Bollington v Heaton Mersey | 18950000 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950000 | match information |
| 50 | Castleton v Stockport | 18950727 | match information |
| 50 | G H Ling's XI v Cheshire | 18950000 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans 1st XI | 18950000 | match information |
| 50 | Macclesfield v Poynton | 18950000 | match information |
| 50 | Phoenix v Manchester South End | 18950000 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950000 | match information |
| 50 | St Matthew's v Hanover 2nd XI | 18950000 | match information |
| 50 | St Thomas' Athletic v Norbury 2nd XI | 18950000 | match information |
| 50 | Stockport Congregational v Raddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950000 | match information |
| 51 | Bollington 2nd XI v Bugsworth | 18950800 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950800 | match information |
| 51 | Kersal v Heaton Mersey | 18950800 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950809 | match information |
| 51 | Stockport v Great Moor | 18950800 | match information |
| 52 | Bollington 2nd XI v Bosworth | 18950800 | match information |
| 52 | Phoenix v Martinrigg | 18950800 | match information |
| 52 | Stockport v Great Moor | 18950800 | match information |
| 53 | Harpurhey BS v Haslingden Wesleyans Second XI | 18950800 | match information |
| 53 | Manchester v Cheshire Rolling | 18950800 | match information |
| 54 | Bromboro Pool v Police | 18950817 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Soapees v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team aggregates | 18950800 | statistics |
| 55 | Bebington Bible Class v St John's 2nd XI | 18950824 | match information |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Phoenix Second XI v Mossley Second XI | 18950800 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 58 | Liverpool Cricket Club team aggregates | 18950000 | statistics |
| 59 | Park A Team player statistics | 18950000 | statistics |
| 59 | Rock Ferry Second XI player statistics | 18950000 | statistics |
| 60 | Oxton match list | 18950000 | team information |
| 61 | Birkenhead Victoria match list | 18950000 | team information |
| 61 | Birkenhead Victoria player statistics | 18950000 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950914 | match information |
| 61 | Cricket Notes | 18950914 | newspaper cuttings |
| 61 | Formby v New Brighton | 18950914 | match information |
| 61 | Liverpool v Oxton | 18950914 | match information |
| 61 | Oxton match list | 18950000 | team information |
| 61 | Oxton player statistics | 18950000 | statistics |
| 61 | Parkites player statistics | 18950000 | statistics |
| 61 | Rock Ferry match list | 18950000 | team information |
| 61 | Rock Ferry player statistics | 18950000 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950914 | match information |
