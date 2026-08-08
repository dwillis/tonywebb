# Evaluation: qwen35_9b_reconciled vs Willis ground truth

Willis pages covered: 57 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 333/395 (84.3%)**
- Exact-key matches: 254; fuzzy-only matches: 79
- Date agreement (matched pairs, both dated): 267/333 (80.2%)
- Content-type agreement (type-blind matches): 322/322 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 288/333 (86.5%)
- Missed Willis rows: 62
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 111

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 320 | 358 | 89.4% |
| newspaper cuttings | 0 | 2 | 0.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 10 | 30 | 33.3% |
| team information | 1 | 3 | 33.3% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 11 | Dunstable Second XI v Carter's | 18950824 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 19 | T.W. Girdlestone's XI player statistics | 18950800 | statistics |
| 24 | Abingdon player statistics | 18950000 | statistics |
| 25 | Newbury match list | 18950000 | team information |
| 25 | Newbury player statistics | 18950000 | statistics |
| 26 | Burghclere v Adbury House | 18950000 | match information |
| 26 | Speen player statistics | 18950000 | statistics |
| 26 | Stockcross match list | 18950000 | team information |
| 27 | Biscuit Factory team aggregates | 18950000 | statistics |
| 27 | Heckfield v Major Mildmay's XI | 18950910 | match information |
| 27 | Reading Police v Reading Corporation Officials | 18950914 | match information |
| 27 | Royal Berks Seed Establishment player statistics | 18950000 | statistics |
| 27 | St. John's Teachers v St. Stephen's Teachers | 18950918 | match information |
| 27 | Sunningdale School player statistics | 18950000 | statistics |
| 35 | Parish Church Institute v Fenny Stratford | 18950803 | match information |
| 35 | Parish Church Institute v Moulson | 18950805 | match information |
| 39 | Great Missenden v Lee Common | 18950822 | match information |
| 40 | Sutton v Haddenham | 18950727 | match information |
| 40 | Willingham v YMCA Cambridge | 18950727 | match information |
| 41 | Cambridge | 18950803 | newspaper cuttings |
| 41 | Histon and Impington v A Team of the Old Higher Grade | 18950700 | match information |
| 43 | Cambridge | 18950810 | newspaper cuttings |
| 43 | County of Cambridge Police v Borough Police | 18950803 | match information |
| 46 | Levenshulme 2nd XI v Macclesfield 2nd XI | 18950615 | match information |
| 46 | Stockport 2nd XI v Werneth 2nd XI | 18950615 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Bramall 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | 18950810 | match information |
| 51 | Cheadle v Heaton Mersey | 18950810 | match information |
| 51 | Hazel Grove UC v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Phoenix v Manchester | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 53 | Lancashire Hill v Harpurhey Wesleyans | 18950817 | match information |
| 54 | Birkenhead Park v Birkenhead Victoria | 18950821 | match information |
| 54 | Birkenhead Park v Ormskirk | 18950817 | match information |
| 54 | Birkenhead Victoria v New Brighton | 18950817 | match information |
| 54 | Mr Wynne's XI v Mr Griffith's XI | 18950817 | match information |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | 18950817 | match information |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | 18950824 | match information |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | 18950824 | match information |
| 57 | Stockport 2nd XI v Cheadle Hulme 2nd XI | 18950824 | match information |
| 58 | Llandudno v Flint | 18950914 | match information |
| 59 | Birkenhead Park A player statistics | 18950901 | statistics |
| 59 | Birkenhead Park player statistics | 18950901 | statistics |
| 59 | Birkenhead Victoria First XI player statistics | 18950901 | statistics |
| 59 | Liverpool v Oxton | 18950907 | match information |
| 59 | Oxton player statistics | 18950901 | statistics |
| 59 | Rock Ferry player statistics | 18950901 | statistics |
| 59 | St. Aidan's player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |
| 60 | Birkenhead Park First XI player statistics | 18950901 | statistics |
| 60 | Birkenhead Victoria First XI player statistics | 18950901 | statistics |
| 60 | Oxton First XI player statistics | 18950901 | statistics |
| 60 | Oxton Second XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry First XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry Second XI player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 29 | Lechlade player statistics | Lechlade Cricket Club player statistics | 0.8 |
| 54 | Bromborough Pool v Birkenhead Police | Brombro Pool v Birkenhead Victoria | 0.8 |
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 30 | Maidenhead player statistics | Maidenhead Cricket Club player statistics | 0.812 |
| 11 | Dunstable Second XI v Caddington | Town Second XI v Caddington | 0.814 |
| 48 | Garston v Liverpool 3rd | Garston v Liverpool Second | 0.824 |
| 42 | Assistants v Professors and Demonstrators | New Museums Professors & Demonstrators v Assistants | 0.826 |
| 23 | Sutton's Juniors v P. Sutton's XI | R.s.e.c.c. Juniors v P Sutton's XI | 0.828 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn Team | 0.829 |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | Biscuit Factory B XI v White Cross | 0.829 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 40 | Married v Single | XI Married v XI Single | 0.842 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir, Bourn End v Little Marlow | 0.845 |
| 4 | Houghton Married v Single | Houghton Married v Houghton Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 57 | Langley v Bollington | Langley v Bollington Second | 0.851 |
| 53 | Lancashire Hill SS v Harpurhey Wesleyans 2nd XI | Lancashire-Hill SS v Harpurhey Wesleyans | 0.867 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second v Stockport Lads' Club First | 0.887 |
| 54 | Worcestershire v Cheshire | Cheshire v Worcester | 0.889 |
| 59 | Bromborough v Spital | Bromborough Pool v Spital | 0.889 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire Hill Second v Stockport Lads' Club First | 0.907 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 5 | LCR Thring | L C R Thring | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 52 | Bramall 1st XI v Stockport 2nd XI | Bramall First v Stockport Second | 0.914 |
| 56 | Didsbury 2nd XI v Poynton 2nd XI | Didsbury Second v Poynton Second | 0.914 |
| 57 | Didsbury 2nd XI v Poynton 2nd XI | Didsbury Second v Poynton Second | 0.914 |
| 6 | Houghton v Westoning | Houghton v Weston | 0.919 |
| 52 | Poynton 2nd XI v Great Moor 2nd XI | Poynton Second v Great Moor Second | 0.919 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory B XI v Causton's Athletic London | 0.92 |
| 52 | Hanover 2nd XI v Heywood's Excelsior 2nd XI | Hanover Second v Heywood Excelsior Second | 0.921 |
| 53 | Grey Horse v New Zealand Chief | Grey Horse v New Zealand Chief Team | 0.923 |
| 3 | Sewers Lime Works v Blows Down Lime Works | Sowell Lime Works v Blows Down Lime Works | 0.927 |
| 56 | Stockport 2nd XI v Cheadle Hulme 2nd XI | Stockport Second v Cheadle Hulme Second | 0.929 |
| 55 | St Mary's 2nd XI v Tranmere Wesley 2nd XI | St Mary's Second v Tranmere Wesley Second | 0.93 |
| 61 | Rock Ferry 2nd XI v Cheadle Hulme 2nd XI | Rock Ferry Second v Cheadle Hulme Second | 0.93 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 51 | Hanover 2nd XI v Heywood's Excelsior 2nd XI | Hanover Second v Heywood's Excelsior Second | 0.933 |
| 49 | Mr G H Ling's XI v Cheadle | G H Ling's XI v Cheadle | 0.936 |
| 45 | Cambridge Borough Police v Cambridge County Police | Cambridge Borough Police v Cambs County Police | 0.938 |
| 46 | Bramall v Bowdon 2nd XI | Bramall v Bowdon Second | 0.939 |
| 46 | Heaton Mersey 2nd XI v South Manchester 2nd XI | Heaton Mersey Second v South Manchester Second | 0.939 |
| 56 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregational Second v Longsight Third | 0.942 |
| 57 | Stockport Congregational 2nd XI v Longsight 3rd XI | Stockport Congregational Second v Longsight Third | 0.942 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Lever-Shulme | 0.943 |
| 61 | Tranmere Wesley v West Derby 2nd XI | Transmere Wesley v West Derby Second | 0.946 |
| 49 | St Matthew's v Hanover 2nd XI | St Matthew's v Hanover Second | 0.949 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 7 | Houghton v Westonings | 18950812 | match information |
| 8 | Luton Volunteers v Rest Of Battalion | 18950810 | match information |
| 11 | Town Second XI v Carter's | 18950824 | match information |
| 14 | All Saints'.oc v Boys' Brigade (first Wokingham Company) Second XI | 18950518 | match information |
| 15 | Earley St. Peter's | 18950518 | team information |
| 16 | Reading School First Eleven player statistics | 18950802 | statistics |
| 16 | Reading School Second Eleven player statistics | 18950802 | statistics |
| 16 | Reading School team aggregates | 18950802 | statistics |
| 18 | Reading | 18950000 | team information |
| 18 | Reading | 18950810 | statistics |
| 18 | Reading v Hounslow Garrison | 18950809 | match information |
| 18 | Sunningdale School match list | 18950000 | team information |
| 19 | Mr T W Girdlestone's XI | 18950000 | statistics |
| 24 | Abingdon Cricket and Football Club | 18950907 | statistics |
| 24 | Abingdon Cricket and Football Club Second Eleven | 18950907 | statistics |
| 25 | Newbury | 18950900 | team information |
| 25 | Newbury Cricket Club match list | 18950713 | team information |
| 25 | Newbury Cricket Club player statistics | 18950900 | statistics |
| 25 | Newbury Cricket Club team aggregates | 18950900 | statistics |
| 26 | Burghclere v Newtown | 18950000 | match information |
| 26 | Speen | 18950000 | team information |
| 26 | Stockcross | 18950000 | team information |
| 26 | Stockcross player statistics | 18950000 | statistics |
| 27 | 49th Regimental District | 18950913 | team information |
| 27 | Royal Berks Seed Establishment team aggregates | 18950000 | statistics |
| 29 | Lechlade | 18951031 | team information |
| 32 | Church Room | 18950719 | team information |
| 32 | St. John's | 18950713 | team information |
| 32 | The Wycombe Y.M.C.A. | 18950713 | team information |
| 33 | Burnham v Slough | 18950803 | team information |
| 33 | Wooburn | 18950803 | team information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 35 | Parish Church v Fenny Stratford S Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 37 | Great Kingshill v Lane End | 18950814 | match information |
| 39 | Mr. Collins' Class | 18950824 | team information |
| 39 | Wycombe Y.M.C.A. | 18950824 | team information |
| 40 | Twelve Of Haddenham v Mr Hoare's XI Of Sutton | 18950727 | match information |
| 40 | YMCA v Willingham | 18950727 | match information |
| 41 | Cambridge County | 18950729 | team information |
| 41 | Cambridge County Cricket Club player statistics | 18950000 | statistics |
| 41 | Histon And Impington v Old Higher Grade | 18950726 | match information |
| 41 | Sawston | 18950727 | match information |
| 42 | Cambridge County Council | 18950800 | team information |
| 42 | Cambridge County Council player statistics | 18950800 | statistics |
| 42 | Cambridge Town Council | 18950800 | team information |
| 42 | Cambridge Town Council player statistics | 18950800 | statistics |
| 43 | Cambridge Express | 18950810 | newspaper cuttings |
| 43 | County v Borough Police | 18950807 | match information |
| 43 | K. S. Ranjitsinhji | 18950810 | biography |
| 46 | Levenshulme v Macclesfield (second Elevens) | 18950615 | match information |
| 46 | Stockport v Werneth (second Elevens) | 18950615 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | Castleton v Stockport | 18950727 | match information |
| 50 | G H Ling's XI v Cheadle | 18950727 | match information |
| 50 | Lancashire Hill SS v Haughton Wesleyans First | 18950727 | match information |
| 50 | Macclesfield v Poynton | 18950727 | match information |
| 50 | Phoenix v Manchester South End | 18950727 | match information |
| 50 | Reddish Vale v Denton Wesleyans | 18950727 | match information |
| 50 | St Matthew's v Hanover Second | 18950727 | match information |
| 50 | St Thomas' Athletic v Norbury Second | 18950727 | match information |
| 50 | Stockport Congregational v Reddish St Elisabeth's | 18950727 | match information |
| 50 | Stockport Great Moor v Strines | 18950727 | match information |
| 50 | Urmston v Bramall | 18950727 | match information |
| 51 | Bollington Second v Bugsworth | 18950814 | match information |
| 51 | Bramall First v Stockport Second | 18950814 | match information |
| 51 | Cheadle Hulme v Sale (second Elevens) | 18950814 | match information |
| 51 | Hazel Grove v Hazel Grove Tradesmen | 18950814 | match information |
| 51 | Kersal v Heaton Mersey | 18950814 | match information |
| 51 | Phoenix v Martretes | 18950814 | match information |
| 51 | Stockport v Great Moor | 18950814 | match information |
| 52 | Bollington Second v Bugsworth | 18950816 | match information |
| 52 | Cheadle Hulme v Sale Second Elevens | 18950816 | match information |
| 52 | Phoenix v Marterers | 18950816 | match information |
| 52 | Stockport v Great Moor | 18950816 | match information |
| 54 | Ormskirk v Park | 18950816 | match information |
| 54 | Park v Victoria | 18950821 | match information |
| 54 | Victoria v New Brighton | 18950817 | match information |
| 54 | Wynne's Team v Griffith's Team | 18950817 | match information |
| 55 | Bebington Bible Class v St John's Second | 18950817 | match information |
| 55 | Liverpool v Rock Ferry (second Elevens) | 18950817 | match information |
| 56 | Cheetham v Levenshulme Second Elevens | 18950000 | match information |
| 57 | Cheetham v Levenshulme Second Elevens | 18950817 | match information |
| 57 | Middlesex v Lancashire | 18950817 | match information |
| 58 | Birkenhead Victoria | 18950913 | statistics |
| 58 | Formby | 18950913 | statistics |
| 58 | Liverpool | 18950913 | statistics |
| 58 | Liverpool v Flint | 18950907 | match information |
| 58 | Northern | 18950913 | statistics |
| 58 | Prescot | 18950913 | statistics |
| 59 | A Match Between Liverpool And Oxton | 18950913 | match information |
| 59 | Birkenhead Park | 18950000 | statistics |
| 59 | Birkenhead Park | 18950907 | team information |
| 59 | Birkenhead Park | 18950914 | team information |
| 59 | Birkenhead Victoria 1st Eleven | 18950000 | statistics |
| 59 | Oxon | 18950000 | statistics |
| 59 | Rock Ferry | 18950000 | statistics |
| 59 | St. Aidan's | 18950000 | statistics |
| 60 | Birkenhead Park | 18950900 | statistics |
| 60 | Birkenhead Victoria First Eleven | 18950900 | statistics |
| 60 | Oxton | 18950900 | statistics |
| 60 | Oxton Second Eleven | 18950900 | statistics |
| 60 | Rock Ferry First Eleven | 18950900 | statistics |
| 60 | Rock Ferry Second Eleven | 18950900 | statistics |
| 61 | Birkenhead Victoria team aggregates | 18950907 | statistics |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton player statistics | 18950907 | statistics |
| 61 | Rock Ferry team aggregates | 18950907 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
