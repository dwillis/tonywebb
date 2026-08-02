# Evaluation: qwen3.5_cloud vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 348/388 (89.7%)**
- Exact-key matches: 235; fuzzy-only matches: 113
- Date agreement (matched pairs, both dated): 233/338 (68.9%)
- Content-type agreement (type-blind matches): 343/343 (100.0%)
- Missed Willis rows: 40
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 111

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 315 | 350 | 90.0% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 25 | 30 | 83.3% |
| team information | 4 | 4 | 100.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
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
| 40 | Sawston v Old Higher Grade | 18950727 | match information |
| 42 | Assistants v Professors and Demonstrators | 18950810 | match information |
| 43 | County of Cambridge Police v Borough Police | 18950803 | match information |
| 46 | Langley v Leek Highfield | 18950615 | match information |
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
| 54 | Liverpool v Rock Ferry | 18950817 | match information |
| 54 | Worcestershire v Cheshire | 18950819 | match information |
| 56 | Bollington Fairfield v Bollington | 18950824 | match information |
| 57 | Phoenix v Cornbrook | 18950824 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |
| 59 | Formby v New Brighton | 18950907 | match information |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 26 | Bradfield v A. Sutton's XI | Milfield v Mr A Sutton's XI | 0.8 |
| 29 | Lechlade player statistics | Lechlade Cricket Club player statistics | 0.8 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce XI v Southall | 0.8 |
| 52 | Kersal v Heaton Mersey | Kersal v Hanover Mersey | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 58 | Liverpool player statistics | Liverpool Cricket Club player statistics | 0.806 |
| 54 | Birkenhead Victoria v New Brighton | Victoria v New Brighton | 0.807 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Lavenhulme Second XI | 0.822 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 27 | Biscuit Factory player statistics | Biscuit Factory Cricket Club player statistics | 0.835 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Brethoven | 0.836 |
| 60 | Oxton First XI player statistics | Oxton Player Statistics | 0.836 |
| 57 | Seymour Mead's v Stockport Post Office | Sixworks Men's v Stockport Post Office | 0.838 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Chadle Hulme v Sale Second XI | 0.841 |
| 4 | Mr. Haviland's XI v Luton Villa Road | Mr R H Haviland's XL v Luton Villa-Road C O | 0.842 |
| 51 | Cheadle v Heaton Mersey | Kersal v Heaton Mersey | 0.844 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill BS v Harpurhey Wesleyans | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Marks Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 41 | Histon and Impington v A Team of the Old Higher Grade | Histon And Impington v Old Higher Grade | 0.848 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 49 | Mr G H Ling's XI v Cheadle | Mr G H Lloyd's XI v Cheadle | 0.863 |
| 51 | Phoenix v Manchester | Phoenix v Masters | 0.865 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 33 | Berkley's XI v Greaves' XI | Mr Berkley XI v Mr Greaves XI | 0.868 |
| 18 | Reading v C.E. Keyser's XI | Reading v Mr C E Keymer's XI | 0.88 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park Player Statistics | 0.88 |
| 27 | Royal Berks Seed Establishment player statistics | Royal Berks Seed Establishment Cricket Club player statistics | 0.881 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second v Stockport Lads' Club First | 0.887 |
| 26 | Stockcross v Chieveley | Stockcross v Chilterley | 0.889 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | Mr T W Girdlestone's XI v Gindlestones Charterhouse | 0.891 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 37 | Long Crendon v Dinton | Long Crendon v Biston | 0.905 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservatives Club | 0.911 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second XI v Longsight Second XI | 0.911 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 37 | Quarterman's Firm v R Ford's Firm | Mr Quarterman's Firm v Mr R Ford's Firm | 0.912 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Third XI v South Manchester Second XI | 0.913 |
| 52 | Bramall 1st XI v Stockport 2nd XI | Bramall First v Stockport Second | 0.914 |
| 59 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria First Eleven player statistics | 0.917 |
| 52 | Poynton 2nd XI v Great Moor 2nd XI | Poynton Second v Great Moor Second | 0.919 |
| 59 | Bromborough v Spital | Bromboro v Spital | 0.919 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory B XI v Causton's Athletic London | 0.92 |
| 20 | Newbury v C.E. Keyser's XI | Newbury v Mr C E Keyser's XI | 0.92 |
| 33 | Rayners XI v Permanent Staff of the 3rd Batt. Oxford Light Infantry | Bayners XI v Permanent Staff Of The Second Batt Oxford Light Infantry | 0.92 |
| 2 | Waterlow's v Aylesbury Printing Works | Waterlow's OC v Aylesbury Printing Works' OC | 0.923 |
| 34 | Wycombe Y.M.C.A. v A. Gray's XI | Wycombe YMCA v Mr A Gray XI | 0.923 |
| 34 | Taplow Station v Bryanston Square | Taplow Station v Baylston Square | 0.923 |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | Wycombe Bells v Wanderers V Holloway's Boot Operatives O C | 0.929 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 33 | J. Grenfell's XI v Beaconsfield | Mr J Grenfell XI v Beaconsfield | 0.933 |
| 52 | Hanover 2nd XI v Heywood's Excelsior 2nd XI | Hanover Second v Heywood's Excelsior Second | 0.933 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill S S v Haughton Wesleyans First XI | 0.938 |
| 2 | F. Gentle's XI v Waterlow's | F Gentle's XI v Waterlow's OC | 0.941 |
| 21 | Burghclere v Adbury House | Burghclere v Ashbury House | 0.941 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 59 | YMCA v Ravenscroft | YMCA v Raverscroft | 0.944 |
| 54 | St Mary's v Tranmere Wesley | St Mary's v Tranmere Wesleyans | 0.945 |
| 52 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Reddish v St Thomas' Hyde | 0.946 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane Addington | 0.946 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |
| 20 | Gentlemen of Berkshire v C.D. Rose's XI | Gentlemen Of Berkshire v Mr C D Rose's XI | 0.947 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 26 | Shepherd's XI v Woolley Park | Mr Shepherd's XI v Woolley Park | 0.947 |
| 33 | High Wycombe v E. Stevens' XI | High Wycombe v Mr E Stevens XI | 0.947 |
| 38 | Marlow v J Monro Walker's XI | Marlow v Mr J Monro Walker's XI | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton Married v Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's Luton | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of Third Volunteer Battalion | 18950814 | match information |
| 11 | Town Second XI v Carter | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950525 | match information |
| 13 | Reading Observer | 18950525 | newspaper cuttings |
| 14 | All Saints' OC v Boys' Brigade Second Wokingham Company Second XI | 18950518 | match information |
| 16 | Reading School First XI player statistics | 18950715 | statistics |
| 16 | Reading School Second XI player statistics | 18950715 | statistics |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Reading | 18950810 | newspaper cuttings |
| 18 | Sunningdale School | 18950000 | team information |
| 18 | Sunningdale School bowling statistics | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club | 18950907 | team information |
| 24 | Abingdon Cricket and Football Club First XI player statistics | 18950907 | statistics |
| 24 | Abingdon Cricket and Football Club Second XI | 18950907 | team information |
| 24 | Abingdon Cricket and Football Club Second XI player statistics | 18950907 | statistics |
| 26 | Buckingham v Newtown |  | match information |
| 26 | Newtown match list | 18950912 | team information |
| 26 | Speen team information | 18950912 | team information |
| 27 | 49th Regimental District CC team aggregates | 18950000 | statistics |
| 27 | Biscuit Factory | 18950000 | team information |
| 27 | Royal Berks Seed Establishment | 18950000 | team information |
| 29 | Lechlade | 18951031 | team information |
| 30 | Maidenhead team aggregates | 18950000 | statistics |
| 32 | Wycombe | 18950719 | newspaper cuttings |
| 33 | Saturday fixtures | 18950810 | fixture information |
| 34 | Gerrards Cross v Osborne Stevens And Co | 18950731 | match information |
| 34 | Wycombe Marsh PL | 18950730 | organisation information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford S Martin | 18950803 | match information |
| 36 | Cippenham v Carlton | 18950805 | match information |
| 37 | Great Kingshill v Lane End | 18950817 | fixture information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 40 | Old Higher Grade v Sawston | 18950727 | match information |
| 41 | Cambridge | 18950803 | newspaper cuttings |
| 41 | Histon And Impington v Old Higher Grade | 18950800 | match information |
| 42 | Professors & Demonstrators v Assistants | 18950810 | match information |
| 43 | County v Borough Police | 18950807 | match information |
| 43 | Kumar Shri Ranjitsinhji | 18950810 | biography |
| 46 | Langley v Lane End | 18950615 | match information |
| 48 | Garston v Liverpool Second XI |  | match information |
| 50 | Bollington v Heaton Mersey |  | match information |
| 50 | Brinksway Sunday School v Meadow |  | match information |
| 50 | Castleton v Stockport | 18950727 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First XI |  | match information |
| 50 | Macclesfield v Poynton |  | match information |
| 50 | Mr G H Ling's XI v Cheshire |  | match information |
| 50 | Phoenix v Manchester South End |  | match information |
| 50 | Reddish Vale v Denton Wesleyans |  | match information |
| 50 | St Matthew's v Hanover Second XI |  | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Urmston v Bramall |  | match information |
| 51 | Bollington Second XI v Bugsworth | 18950800 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950816 | match information |
| 51 | Bollington v Sandbach | 18950816 | match information |
| 51 | Bramall First XI v Stockport Second XI | 18950816 | match information |
| 51 | Cheadle Hulme v Hale Second XI | 18950816 | match information |
| 51 | Hanover Second XI v Heywood Excelsior Second XI | 18950816 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950816 | match information |
| 51 | Kersal v Heaton Mersey | 18950816 | match information |
| 51 | Lancashire-Hill Second XI v Stockport Lads Club First XI | 18950816 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950800 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950816 | match information |
| 51 | Phoenix v Marsters | 18950800 | match information |
| 51 | St Joseph Handen v St Thomas Hyde | 18950810 | match information |
| 51 | St Joseph's Handen v St Thomas' Hyde | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950800 | match information |
| 51 | Stockport v Great Moor | 18950816 | match information |
| 51 | Stockport v Little Lever | 18950816 | match information |
| 52 | Bollington Second XI v Bosworth | 18950816 | match information |
| 52 | Phoenix v Martinrigg | 18950816 | match information |
| 52 | Stockport v Great Moor | 18950816 | match information |
| 53 | Harpurhey BS v Haslingden Wesleyans Second XI | 18950817 | match information |
| 53 | Manchester v Cheshire Rolling | 18950817 | match information |
| 54 | Birkenhead | 18950824 | newspaper cuttings |
| 54 | Bromboro Pool v Police | 18950817 | match information |
| 54 | Cheshire v Worcestershire | 18950800 | match information |
| 54 | New Brighton v Liverpool | 18950821 | match information |
| 54 | Ormskirk v The Park | 18950817 | match information |
| 54 | Rock Ferry v Liverpool | 18950817 | match information |
| 54 | Soapees v Helsby | 18950817 | match information |
| 54 | The Park v Victoria | 18950821 | match information |
| 54 | Woodland team aggregates | 18950800 | statistics |
| 55 | All Saints v Wesleyites | 18950824 | match information |
| 55 | St John's Second XI v Bebington Bible Class | 18950824 | match information |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Phoenix Second XI v Mossley Second XI | 18950824 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 58 | Liverpool Cricket Club team aggregates | 18950000 | statistics |
| 59 | Birkenhead | 18950914 | newspaper cuttings |
| 59 | Birkenhead Park team aggregates | 18950000 | statistics |
| 59 | Birkenhead Victoria First Eleven team aggregates | 18950000 | statistics |
| 59 | New Brighton v Formby | 18950914 | match information |
| 59 | Oxton team aggregates | 18950000 | statistics |
| 59 | Park A Team player statistics | 18950000 | statistics |
| 59 | Rock Ferry Second XI player statistics | 18950000 | statistics |
| 59 | Rock Ferry Second XI team aggregates | 18950000 | statistics |
| 59 | Rock Ferry team aggregates | 18950000 | statistics |
| 59 | St Aidan team aggregates | 18950000 | statistics |
| 60 | Oxton Match List | 18950000 | team information |
| 61 | Birkenhead News | 18950914 | newspaper cuttings |
| 61 | Bootle v Birkenhead Victoria | 18950914 | match information |
| 61 | Formby v New Brighton | 18950914 | match information |
| 61 | Liverpool v Oxton | 18950914 | match information |
| 61 | Rock Ferry v Cheadle Hulme | 18950914 | match information |
