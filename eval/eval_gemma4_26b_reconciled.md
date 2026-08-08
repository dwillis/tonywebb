# Evaluation: gemma4_26b_reconciled vs Willis ground truth

Willis pages covered: 57 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 358/395 (90.6%)**
- Exact-key matches: 280; fuzzy-only matches: 78
- Date agreement (matched pairs, both dated): 293/358 (81.8%)
- Content-type agreement (type-blind matches): 354/354 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 286/358 (79.9%)
- Missed Willis rows: 37
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 103

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 328 | 358 | 91.6% |
| newspaper cuttings | 1 | 2 | 50.0% |
| player information | 0 | 1 | 0.0% |
| statistics | 27 | 30 | 90.0% |
| team information | 1 | 3 | 33.3% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 3 | Houghton Married v Houghton Single | 18950805 | match information |
| 4 | Haviland's XI v Luton Villa Road | 18950803 | match information |
| 13 | Biscuit Factory Stores Married v Biscuit Factory Stores Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 16 | Reading School match list | 18950802 | team information |
| 16 | Reading School players | 18950802 | player information |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | 18950727 | match information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 24 | Abingdon player statistics | 18950000 | statistics |
| 25 | Newbury match list | 18950000 | team information |
| 25 | Newbury player statistics | 18950000 | statistics |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 37 | Quarterman's Firm v R Ford's Firm | 18950808 | match information |
| 38 | Wycombe Belle Vue Wanderers v Holloway's Boot Operatives CC | 18950824 | match information |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 43 | Cambridge | 18950810 | newspaper cuttings |
| 43 | County of Cambridge Police v Borough Police | 18950803 | match information |
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
| 53 | Lancashire Hill v Harpurhey Wesleyans | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 56 | Stockport 2nd XI v Cheadle Hulme 2nd XI | 18950824 | match information |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 54 | Bromborough Pool v Birkenhead Police | Bromboro Pool v Birkenhead Victoria | 0.817 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second | 0.817 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | T W Girdlestone's XI v Girdlestoneites | 0.818 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town v Aston Clinton | 0.844 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 46 | Stockport 2nd XI v Werneth 2nd XI | Stockport v Werneth Second XI | 0.853 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 35 | Parish Church Institute v Fenny Stratford | Parish Church v Fenny Stratford | 0.861 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 21 | Burghclere v Adbury House | Burghclere v Adbury | 0.864 |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | Rock Ferry v Liverpool Second XI | 0.865 |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Beethoven | 0.866 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill SS v Harpurhey Wesleyans | 0.867 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 4 | Waterlow's v St Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 21 | A.W. Baker's Hagbourne Team v A.F. Clarke's Wantage Team | A W Baker's Team v A F Clarke's Wantage Team | 0.87 |
| 42 | Assistants v Professors and Demonstrators | New Museums Professors And Demonstrators v Assistants | 0.872 |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | Levenshulme v Macclesfield Second XI | 0.878 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 54 | Worcestershire v Cheshire | Cheshire v Worcester | 0.889 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Mr Wynne's v Mr Griffith's | 0.889 |
| 59 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 56 | Chorlton A Team v Macclesfield Conservative Club | Chorlton Second v Macclesfield Conservative Club | 0.896 |
| 33 | High Wycombe v E. Stevens' XI | Wycombe v E Stevens' XI | 0.898 |
| 49 | Lancashire Hill SS v Haughton Wesleyans 1st XI | Lancashire Hill SS v Haughton Wesleyans Second XI | 0.907 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 59 | Birkenhead Park A player statistics | Birkenhead Park "A" team player statistics | 0.909 |
| 56 | Didsbury 2nd XI v Poynton 2nd XI | Didsbury Second v Poynton Second | 0.914 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 3 | Sewers Lime Works v Blows Down Lime Works | Sowell Lime Works v Blows Down Lime Works | 0.927 |
| 57 | Stockport 2nd XI v Cheadle Hulme 2nd XI | Stockport Second v Cheadle Hulme Second | 0.929 |
| 61 | Rock Ferry 2nd XI v Cheadle Hulme 2nd XI | Rock Ferry Second v Cheadle Hulme Second | 0.93 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 26 | Southington v A. Kingsmill's XII | Southington v Mr A Kingsmill's XI | 0.935 |
| 49 | Mr G H Ling's XI v Cheadle | G H Ling's XI v Cheadle | 0.936 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Second v South Manchester Second | 0.939 |
| 56 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregational Second v Longsight Third | 0.942 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Lever-Shulme | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 53 | Langley v Crossley's | Langley v Crosley | 0.944 |
| 19 | T.W. Girdlestone's XI player statistics | Mr T W Girdlestone's XI player statistics | 0.947 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 3 | Single v Married | 18950805 | match information |
| 4 | R H Haviland's XI v Luton Villa-Road | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 8 | Luton Volunteers v Rest Of Battalion | 18950810 | match information |
| 13 | Biscuit Factory Stores Married v Single | 18950518 | match information |
| 14 | All Saints' v Boys' Brigade (first Wokingham Company) Second XI | 18950518 | match information |
| 15 | Earley St. Peter's | 18950518 | team information |
| 16 | Reading School Cricket Club match list | 18950000 | team information |
| 16 | Reading School Cricket Club player statistics | 18950000 | statistics |
| 16 | Reading School Cricket Club players | 18950000 | player information |
| 16 | Reading School Cricket Club team aggregates | 18950000 | statistics |
| 17 | Biscuit Factory v White Cross | 18950727 | match information |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Reading v Hounslow Garrison | 18950809 | match information |
| 24 | Abingdon Cricket and Football Club | 18950000 | team information |
| 24 | Abingdon Cricket and Football Club Second XI player statistics | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club Second XI team aggregates | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club player statistics | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club team aggregates | 18950000 | statistics |
| 25 | Newbury Cricket Club match list | 18950000 | team information |
| 25 | Newbury Cricket Club player statistics | 18950000 | statistics |
| 25 | Newbury Cricket Club team aggregates | 18950000 | statistics |
| 26 | Burghclere v Newtown | 18950000 | match information |
| 26 | Newtown team aggregates | 18950000 | statistics |
| 26 | Stockcross team aggregates | 18950000 | statistics |
| 27 | 49th Regimental District team aggregates | 18950000 | statistics |
| 27 | N.C. Officers and Men's XI team aggregates | 18950000 | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 30 | Maidenhead team aggregates | 18950000 | statistics |
| 32 | Church Room | 18950719 | team information |
| 32 | St John's | 18950719 | team information |
| 32 | Wycombe Club | 18950718 | team information |
| 32 | Wycombe First XI | 18950000 | team information |
| 32 | Wycombe YMCA | 18950713 | team information |
| 33 | Blythewood v Cippenham match list | 18950803 | team information |
| 33 | Burnham v Slough match list | 18950803 | team information |
| 33 | Taplow Station v Reading Temperance match list | 18950803 | team information |
| 33 | Wooburn | 18950803 | team information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 34 | Wycombe Marsh F.C. | 18950730 | team information |
| 34 | Wycombe Y.M.C.A. match list | 18950803 | team information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton | 18950805 | match information |
| 37 | Quarterman's Firm v Ford's Firm | 18950808 | match information |
| 38 | Belle Vue Wanderers v Holloway's Boot Operatives | 18950824 | match information |
| 39 | Mr Collins' Class match list | 18950824 | team information |
| 39 | Wycombe YMCA match list | 18950824 | team information |
| 41 | Cambridge County | 18950731 | team information |
| 41 | Histon And Impington v Old Higher Grade | 18950727 | match information |
| 41 | Sawston v Old Higher Grade | 18950727 | match information |
| 43 | Cambs Cricket Association Cup | 18950000 | newspaper cuttings |
| 43 | Cambs Cricket Eleven | 18950000 | newspaper cuttings |
| 43 | County v Borough Police | 18950807 | match information |
| 43 | K S Ranjitsinhji | 18950000 | biography |
| 43 | K S Ranjitsinhji | 18950000 | newspaper cuttings |
| 43 | Leading dozen batsmen player statistics | 18950803 | statistics |
| 43 | Tom Hayward | 18950000 | newspaper cuttings |
| 48 | Garston v Liverpool Second XI | 18950000 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | Castleton v Stockport | 18950000 | newspaper cuttings |
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
| 51 | Stockport v Great Moor | 18950810 | match information |
| 52 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 52 | Phoenix v Marterers | 18950810 | match information |
| 52 | Stockport v Great Moor | 18950810 | match information |
| 52 | Werneth v Cale Green | 18950810 | fixture information |
| 54 | Ormskirk v Park | 18950822 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Soapees v Helsby | 18950817 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 55 | All Saints | 18950000 | team information |
| 55 | Bebington Bible Class v St John's Second XI | 18950817 | match information |
| 56 | St Thomas' Athletic | 18950831 | team information |
| 56 | Stockport And Cheadle Hulme Second v Cheadle Hulme Second | 18950824 | match information |
| 57 | Middlesex v Lancashire | 18950000 | match information |
| 57 | Reddish St Joseph's team aggregates | 18950000 | statistics |
| 57 | St Thomas' Athletic | 18950831 | team information |
| 59 | Oxton match list | 18950000 | team information |
| 59 | Rock Ferry Second XI player statistics | 18950000 | statistics |
| 60 | Oxton match list | 18950000 | team information |
| 61 | Birkenhead Victoria player statistics | 18950000 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool player statistics | 18950000 | statistics |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950000 | statistics |
| 61 | Rock Ferry player statistics | 18950000 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
