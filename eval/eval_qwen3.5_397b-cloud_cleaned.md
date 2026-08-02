# Evaluation: qwen3.5_397b-cloud_cleaned vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 339/388 (87.4%)**
- Exact-key matches: 252; fuzzy-only matches: 87
- Date agreement (matched pairs, both dated): 246/321 (76.6%)
- Content-type agreement (type-blind matches): 337/337 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 291/339 (85.8%)
- Missed Willis rows: 49
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 80

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 309 | 350 | 88.3% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 26 | 30 | 86.7% |
| team information | 0 | 4 | 0.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 16 | Reading School match list | 18950802 | team information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | 18950731 | match information |
| 25 | Newbury match list | 18950000 | team information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 26 | Stockcross match list | 18950000 | team information |
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
| 52 | Kersal v Heaton Mersey | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 53 | Lancashire Hill v Harpurhey Wesleyans | 18950817 | match information |
| 53 | Manchester v Cheadle Hulme | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Bromborough Pool v Birkenhead Police | 18950817 | match information |
| 54 | Woodland v Kingsley | 18950819 | match information |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | 18950817 | match information |
| 56 | Bollington Fairfield v Bollington | 18950824 | match information |
| 57 | Phoenix v Cornbrook | 18950824 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |
| 60 | Rock Ferry Second XI player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 26 | Stockcross v Chieveley | Stockcross v Chilterny | 0.818 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Lavenhulme Second XI | 0.822 |
| 51 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Handen v St Thomas' (hyde) | 0.827 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Brethoven | 0.836 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 57 | Seymour Mead's v Stockport Post Office | Sixworks Men's v Stockport Post Office | 0.838 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Chadle Hulme v Sale Second XI | 0.841 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill BS v Harpurhey Wesleyans | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 26 | Bradfield v A. Sutton's XI | Milfield v A Sutton's XI | 0.851 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 56 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 57 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 51 | Phoenix v Manchester | Phoenix v Masters | 0.865 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 4 | Mr. Haviland's XI v Luton Villa Road | R H Haviland's XI v Luton Villa-Road CO | 0.889 |
| 54 | Worcestershire v Cheshire | Cheshire v Worcester | 0.889 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Wynne's XI v Griffith's XI | 0.889 |
| 34 | Taplow Station v Bryanston Square | Taplow Station v Baylston-Square | 0.892 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 37 | Long Crendon v Dinton | Long Crendon v Biston | 0.905 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second XI v Longsight Second XI | 0.911 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Third XI v South Manchester Second XI | 0.913 |
| 59 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria First Eleven player statistics | 0.917 |
| 53 | Hollinwood v Marple | Hollinwood v Mamle | 0.919 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 18 | Reading v C.E. Keyser's XI | Reading v C E Keymer's XI | 0.936 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 26 | Speen player statistics | Speen C.C. player statistics | 0.939 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane Addington | 0.946 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill SS v Haughton Wesleyans First XI | 0.947 |
| 50 | Reddish St Joseph's v Union Street Hyde | Raddish St Joseph's v Union-Street Hyde | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton CC Married v Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of The Third Volunteer Battalion | 18950807 | match information |
| 11 | Town Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade Second Wokingham Company Second XI | 18950518 | match information |
| 16 | Reading School player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Hounslow Garrison v Reading | 18950809 | match information |
| 19 | T W Girdlestone's XI v Gindlestones | 18950731 | match information |
| 25 | Newbury team aggregates | 18950912 | statistics |
| 26 | Buckingham v Newtown |  | match information |
| 26 | Newtown team aggregates |  | statistics |
| 26 | Stockcross team aggregates |  | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 33 | Bayners XI v Permanent Staff Of The Second Batt Oxford Light Infantry | 18950805 | match information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford S Martin | 18950803 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 37 | Fine Apple v King's Head | 18950805 | match information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 38 | Wycombe Bells v Wanderers V Holloway's Boot Operatives | 18950824 | match information |
| 41 | Histon And Impington v Old Higher Grade | 18950800 | match information |
| 43 | Kumar Shri Ranjitsinhji |  | biography |
| 46 | Langley v Lane End | 18950615 | match information |
| 48 | Garston v Liverpool Second XI | 18950708 | match information |
| 49 | G H Lloyd's XI v Cheadle | 18950727 | match information |
| 49 | Hollington v Heaton Mersey | 18950727 | match information |
| 50 | Bollington v Heaton Mersey | 18950800 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950800 | match information |
| 50 | G H Ling's XI v Cheshire | 18950800 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First XI | 18950800 | match information |
| 50 | Macclesfield v Poynton | 18950800 | match information |
| 50 | Phoenix v Manchester South End | 18950800 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950800 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950800 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950800 | match information |
| 50 | Stockport Congregational v Raddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950800 | match information |
| 51 | Bollington Second XI v Bugsworth |  | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen |  | match information |
| 51 | Kersal v Heaton Mersey |  | match information |
| 51 | Macclesfield v Lever-Daulby |  | match information |
| 51 | Stockport v Great Moor |  | match information |
| 52 | Bollington Second XI v Bosworth | 18950800 | match information |
| 52 | Kersal v Hanover Mershy | 18950800 | match information |
| 52 | Phoenix v Martinrigg | 18950800 | match information |
| 52 | Stockport v Great Moor | 18950800 | match information |
| 53 | Harpurhey BS v Haslingden Wesleyans Second XI | 18950817 | match information |
| 53 | Manchester v Cheshire Rolling | 18950817 | match information |
| 54 | Bromboro Pool v Police | 18950817 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Soapees v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland player statistics | 18950819 | statistics |
| 55 | Bebington Bible Class v St John's Second XI | 18950817 | match information |
| 55 | Liverpool v Rock Ferry Second Elevens | 18950800 | match information |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Phoenix Second XI v Mossley Second XI | 18950824 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 59 | Park A Team player statistics | 18950000 | statistics |
| 59 | Rock Ferry Second XI player statistics | 18950000 | statistics |
| 61 | Birkenhead Park player statistics | 18950914 | statistics |
| 61 | Birkenhead Victoria player statistics | 18950907 | statistics |
| 61 | Birkenhead Victoria team aggregates | 18950907 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950907 | statistics |
| 61 | Oxton team aggregates | 18950907 | statistics |
| 61 | Rock Ferry player statistics | 18950907 | statistics |
| 61 | Rock Ferry team aggregates | 18950907 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
