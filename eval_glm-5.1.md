# Evaluation: glm-5.1 vs Willis ground truth

Willis pages covered: 56 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 348/388 (89.7%)**
- Exact-key matches: 240; fuzzy-only matches: 108
- Date agreement (matched pairs, both dated): 271/348 (77.9%)
- Content-type agreement (type-blind matches): 346/347 (99.7%)
- Missed Willis rows: 40
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 87

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 313 | 350 | 89.4% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 29 | 30 | 96.7% |
| team information | 2 | 4 | 50.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 15 | Earley St. Peter's | 18950500 | team information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 25 | Newbury match list | 18950000 | team information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
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
| 59 | Formby v New Brighton | 18950907 | match information |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 26 | Bradfield v A. Sutton's XI | Milfield v Mr A Sutton's XI | 0.8 |
| 39 | Four Veterans v Four Juniors | Four Veterans v Four Juniors Single Wicket | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood Lanes v Poynton Second XI | 0.806 |
| 54 | Birkenhead Victoria v New Brighton | Victoria v New Brighton | 0.807 |
| 52 | Poynton United v Wood Lane (Adlington) | Poynton United v Wood Lane | 0.812 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Mr Wynne's Team v Mr Griffith's Team | 0.812 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Lavenhulme Second XI | 0.822 |
| 57 | Seymour Mead's v Stockport Post Office | Silkworks Men's v Stockport Post Office | 0.827 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Hale Second XI | 0.829 |
| 16 | Reading School players | Reading School First XI players | 0.83 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Brethoven | 0.836 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 34 | Burnham v Postal Telegraph (London) | Burnham v Postal Telegraphs | 0.839 |
| 34 | Chalfont Park v St. Silas (London) | Chalfont Park v St Silas | 0.842 |
| 51 | Phoenix v Manchester | Phoenix v Marsters | 0.842 |
| 26 | Stockcross v Chieveley | Stockcross v Chilterney | 0.844 |
| 51 | Cheadle v Heaton Mersey | Kersal v Heaton Mersey | 0.844 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill BS v Harpurhey Wesleyans | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservatives | 0.847 |
| 41 | Histon and Impington v A Team of the Old Higher Grade | Histon And Impington v Old Higher Grade | 0.848 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 56 | Chorlton A Team v Macclesfield Conservative Club | Chorlton v Macclesfield Conservative | 0.857 |
| 56 | Lads' Club 2nd XI v St Thomas' Athletic | Lane End Second XI v St Thomas' Athletic | 0.861 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 49 | Mr G H Ling's XI v Cheadle | Mr G H Lloyd's XI v Cheadle | 0.863 |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 33 | Berkley's XI v Greaves' XI | Mr Berkley XI v Mr Greaves XI | 0.868 |
| 57 | Stockport 2nd XI v Cheadle Hulme 2nd XI | Stockport v Cheadle Hulme Second XI | 0.875 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 18 | Reading v C.E. Keyser's XI | Reading v Mr C E Keymer's XI | 0.88 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 42 | Cambridge Town Council v County Council | Cambridge Town Council v Cambridge County Council | 0.886 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads Club First XI | 0.893 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | Mr T W Girdlestone's XI v Girdlestones Charterhouse | 0.911 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregationals Second XI v Longsight Second XI | 0.911 |
| 21 | Newbury v 49th Regimental District | Newbury v 43rd Regimental District | 0.912 |
| 37 | Quarterman's Firm v R Ford's Firm | Mr Quarterman's Firm v Mr R Ford's Firm | 0.912 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancaster Hill SS v Haughton Wesleyans First | 0.913 |
| 4 | Mr. Haviland's XI v Luton Villa Road | Mr R H Haviland's XI v Luton Villa-Road | 0.917 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 59 | Bromborough v Spital | Bromboro v Spital | 0.919 |
| 20 | Newbury v C.E. Keyser's XI | Newbury v Mr C E Keyser's XI | 0.92 |
| 2 | Waterlow's v Aylesbury Printing Works | Waterlow's OC v Aylesbury Printing Works OC | 0.923 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 33 | J. Grenfell's XI v Beaconsfield | Mr J Grenfell XI v Beaconsfield | 0.933 |
| 59 | Birkenhead Park A player statistics | Birkenhead Park A Team player statistics | 0.933 |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | Wycombe Bells v Wanderers V Holloway's Boot Operatives OC | 0.937 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 55 | Dawpool v Laird's Bros Draughtsmen | Dawpool v Laird's Bros Draftsmen | 0.938 |
| 2 | F. Gentle's XI v Waterlow's | F Gentle's XI v Waterlow's OC | 0.941 |
| 21 | Burghclere v Adbury House | Burghclere v Ashbury House | 0.941 |
| 34 | Wycombe Y.M.C.A. v A. Gray's XI | Wycombe YMCA v Mr A Gray's XI | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 59 | YMCA v Ravenscroft | YMCA v Raverscroft | 0.944 |
| 24 | Abingdon player statistics | Abingdon XI player statistics | 0.945 |
| 52 | St Joseph's (Reddish) v St Thomas' (Hyde) | St Joseph's Reddish v St Thomas' Hyde | 0.946 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |
| 20 | Gentlemen of Berkshire v C.D. Rose's XI | Gentlemen Of Berkshire v Mr C D Rose's XI | 0.947 |
| 21 | Wantage v Ardington | Wantage v Andington | 0.947 |
| 26 | Shepherd's XI v Woolley Park | Up Shepherd's XI v Woolley Park | 0.947 |
| 33 | High Wycombe v E. Stevens' XI | High Wycombe v Mr E Stevens XI | 0.947 |
| 38 | Marlow v J Monro Walker's XI | Marlow v Mr J Monro Walker's XI | 0.947 |
| 46 | Bollington v Buxton | Bollington v Huxton | 0.947 |
| 33 | Rayners XI v Permanent Staff of the 3rd Batt. Oxford Light Infantry | Bayners XI v Permanent Staff Of The Iind Batt Oxford Light Infantry | 0.948 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Dunstable Second XI v Markyate Street | 18950803 | match information |
| 4 | Houghton Married v Houghton Single | 18950805 | match information |
| 4 | Waterlow's v St Matthew's Luton | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 7 | Luton Detachment v Remainder Of The Iiird Volunteer Battalion | 18950814 | match information |
| 11 | Town Second XI v Carter's | 18950824 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' OC v Boys' Brigade Second XI | 18950518 | match information |
| 15 | Earley St Peter's | 18950525 | fixture information |
| 16 | Reading School First XI player statistics | 18950715 | statistics |
| 16 | Reading School Second XI player statistics | 18950715 | statistics |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 24 | Abingdon | 18950907 | team information |
| 24 | Abingdon Second XI player statistics | 18950907 | statistics |
| 25 | Newbury | 18950000 | team information |
| 26 | Buckingham v Newtown | 18950000 | match information |
| 27 | 49th Regimental District | 18950000 | team information |
| 27 | Royal Berks Seed Establishment | 18950000 | team information |
| 29 | Lechlade team aggregates | 18951031 | statistics |
| 32 | Wycombe | 18950719 | newspaper cuttings |
| 33 | Saturday Fixtures | 18950810 | fixture information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 34 | Wycombe Marsh PL | 18950730 | organisation information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 35 | Parish Church v Penny Stratford St Martin | 18950803 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 37 | Stokechurch v Shiremill | 18950806 | match information |
| 39 | Mr W Pearce's XI v Southall | 18950824 | match information |
| 40 | Mr Hoare's Sutton XI v Haddenham XII | 18950727 | match information |
| 40 | Old Higher Grade v Sawston | 18950727 | match information |
| 42 | Professors And Demonstrators v Assistants | 18950810 | match information |
| 43 | Cambridgeshire County Police v Cambridgeshire Borough Police | 18950807 | match information |
| 43 | KS Ranjitsinhji | 18950810 | biography |
| 43 | Leading Batsmen player statistics | 18950804 | statistics |
| 46 | Langley v Lane End | 18950615 | match information |
| 48 | Garston v Liverpool Second XI | 18950709 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950802 | match information |
| 50 | Castleton v Stockport | 18950727 | match information |
| 50 | Lancashire Hill Sunday School v Haughton Wesleyans First XI | 18950727 | match information |
| 50 | Macclesfield v Poynton | 18950727 | match information |
| 50 | Mr G H Ling's XI v Cheshire | 18950802 | match information |
| 50 | Phoenix v Manchester South End | 18950802 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950802 | match information |
| 50 | St Matthew's v Hanover Second XI | 18950802 | match information |
| 50 | St Thomas' Athletic v Norbury Second XI | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Sirines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950727 | match information |
| 51 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 51 | Hanover First XI v Heywood's Excelsior First XI | 18950800 | match information |
| 51 | Macclesfield v Lever-Daulby | 18950810 | match information |
| 51 | St Joseph's Handen v St Thomas' Hyde | 18950810 | match information |
| 51 | Stockport v Great Moor | 18950800 | match information |
| 52 | Bollington Second XI v Bosworth | 18950810 | match information |
| 52 | Phoenix v Martinrigg | 18950810 | match information |
| 52 | Stockport v Great Moor | 18950810 | match information |
| 53 | Harpurhey BS v Haslingden Wesleyans Second XI | 18950817 | match information |
| 53 | Manchester v Cheshire Rolling | 18950817 | match information |
| 54 | Birkenhead Advertiser | 18950824 | newspaper cuttings |
| 54 | Bromborough Pool v Police First XI | 18950817 | match information |
| 54 | Cheshire v Worcester | 18950800 | match information |
| 54 | New Brighton v Liverpool | 18950821 | match information |
| 54 | Ormskirk v Park | 18950817 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Rock Ferry v Liverpool | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 55 | All Saints v Tranmere Wesley Second XI | 18950817 | match information |
| 56 | Hollinwood v Fairfield | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Phoenix Second XI v Mossley Second XI | 18950824 | match information |
| 57 | Phoenix v Conservatives | 18950824 | match information |
| 58 | Liverpool team aggregates | 18950000 | statistics |
| 59 | Birkenhead Fixtures | 18950914 | fixture information |
| 59 | New Brighton v Formby | 18950907 | match information |
| 59 | Rock Ferry Second XI player statistics | 18950900 | statistics |
| 59 | Rock Ferry team aggregates | 18950900 | statistics |
| 60 | Oxton match list | 18950900 | team information |
| 61 | Birkenhead Victoria player statistics | 18950914 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950914 | statistics |
| 61 | Park player statistics | 18950914 | statistics |
| 61 | Rock Ferry player statistics | 18950914 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
