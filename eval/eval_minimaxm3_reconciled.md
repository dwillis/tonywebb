# Evaluation: minimaxm3_reconciled vs Willis ground truth

Willis pages covered: 57 (pages 1-61; no claim made about pages outside this range)

- **Willis coverage (recall): 364/395 (92.2%)**
- Exact-key matches: 301; fuzzy-only matches: 63
- Date agreement (matched pairs, both dated): 298/364 (81.9%)
- Content-type agreement (type-blind matches): 362/362 (100.0%)
- Pages-count agreement (matched pairs -- does the model flag the same number of pages this entry spans as Willis does): 284/364 (78.0%)
- Missed Willis rows: 31
- Surplus model rows on Willis-covered pages (review list, NOT false positives -- Willis is partial even within these pages): 87

## Coverage by content type

| Content type | Matched | Total | Coverage |
|---|---:|---:|---:|
| biography | 1 | 1 | 100.0% |
| match information | 332 | 358 | 92.7% |
| newspaper cuttings | 2 | 2 | 100.0% |
| player information | 1 | 1 | 100.0% |
| statistics | 25 | 30 | 83.3% |
| team information | 3 | 3 | 100.0% |

## Missed Willis rows (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | Haviland's XI v Luton Villa Road | 18950803 | match information |
| 14 | All Saints' v Boys' Brigade | 18950518 | match information |
| 17 | Biscuit Factory B XI v White Cross (Basingstoke) | 18950727 | match information |
| 17 | Heath End v McElroy's (Reading) | 18950801 | match information |
| 18 | Reading v Marylebone | 18950805 | match information |
| 26 | Burghclere v Adbury House | 18950000 | match information |
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
| 49 | Castleton v Stockport | 18950727 | match information |
| 50 | Heaton Mersey Sunday School v Meadow Cricket Club | 18950727 | match information |
| 51 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 51 | Cheadle v Heaton Mersey | 18950810 | match information |
| 51 | Hazel Grove UC v Hazel Grove Tradesmen | 18950810 | match information |
| 51 | Phoenix v Manchester | 18950810 | match information |
| 51 | Poynton v Stockport Great Moor | 18950810 | match information |
| 52 | Bollington 2nd XI v Stockport 2nd XI | 18950810 | match information |
| 52 | Phoenix v Manchester | 18950810 | match information |
| 52 | Poynton v Stockport Great Moor | 18950810 | match information |
| 57 | Stockport v Cheadle Hulme | 18950824 | match information |
| 59 | Birkenhead Victoria First XI player statistics | 18950901 | statistics |
| 60 | Birkenhead Park "A" Team player statistics | 18950901 | statistics |
| 60 | Oxton Second XI player statistics | 18950901 | statistics |
| 60 | Rock Ferry Second XI player statistics | 18950901 | statistics |

## Fuzzy matches below 0.95 similarity (review)

| Page | Willis | Model | Similarity |
|---:|---|---|---:|
| 56 | Bollington Fairfield v Bollington | Bollington v Fairfield | 0.8 |
| 57 | Langley v Bollington | Langley v Bollington Second XI | 0.8 |
| 19 | T.W. Girdlestone's XI v Girdlestoneites (Charterhouse) | T W Girdlestone's XI v Girdlestoneites | 0.818 |
| 39 | W Pearce's (Wycombe) XI v Southall | W Pearce's XI v Southall | 0.821 |
| 43 | County of Cambridge Police v Borough Police | County Police v Borough Police | 0.822 |
| 17 | Heath End v St. Laurence's (Reading) | Heath End v St Laurence's | 0.828 |
| 20 | Heath Row v Ipsden | Heath End v Ipsden | 0.833 |
| 46 | Wood-Lanes (Adlington) v Poynton 2nd XI | Wood-Lanes v Poynton Second XI | 0.833 |
| 60 | Oxton First XI player statistics | Oxton player statistics | 0.836 |
| 33 | St. Mark's Choir v Little Marlow | St Mark's Choir Bourne End v Little Marlow | 0.845 |
| 3 | Houghton Married v Houghton Single | Houghton Married v Single | 0.847 |
| 4 | Houghton Married v Single | Houghton Married v Houghton Single | 0.847 |
| 49 | Stockport Great Moor v Summer | Stockport Great Moor v Strines | 0.847 |
| 51 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 52 | Cheadle Hulme 2nd XI v Sale 2nd XI | Cheadle Hulme v Sale Second XI | 0.857 |
| 59 | Birkenhead Park A player statistics | Birkenhead Victoria player statistics | 0.861 |
| 56 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 57 | Reddish Vale v Mr R P Hammond's Team | Reddish Vale v R P Hammond's XI | 0.862 |
| 60 | Rock Ferry First XI player statistics | Rock Ferry player statistics | 0.862 |
| 55 | Liverpool 2nd XI v Rock Ferry 2nd XI | Liverpool v Rock Ferry Second XI | 0.865 |
| 56 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 57 | Cheetham 2nd XI v Levenshulme 2nd XI | Cheetham v Levenshulme Second XI | 0.865 |
| 33 | Wycombe Alexandra v Beethoven (London) | Wycombe Alexandra v Beethoven | 0.866 |
| 3 | Waterlow's v St. Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 4 | Waterlow's v St Matthew's, Luton | Waterlow's v St Matthew's | 0.868 |
| 60 | Birkenhead Park First XI player statistics | Birkenhead Park player statistics | 0.88 |
| 51 | Bramall 2nd XI v Stockport 2nd XI | Bramall First XI v Stockport Second XI | 0.883 |
| 14 | Abbey Wharf v Caversham B XI | Abbey Wharf v Caversham Second XI | 0.885 |
| 54 | Mr Wynne's XI v Mr Griffith's XI | Wynne's XI v Griffith's XI | 0.889 |
| 60 | Birkenhead Victoria First XI player statistics | Birkenhead Victoria player statistics | 0.892 |
| 51 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 52 | Lancashire Hill 2nd XI v Stockport Lads' Club | Lancashire-Hill Second XI v Stockport Lads' Club First XI | 0.893 |
| 3 | Silston v Maulden | Silsoe v Maulden | 0.909 |
| 33 | Amersham v Harlesden | Amersham UCC v Harlesden | 0.909 |
| 20 | Biscuit Factory B XI v Causton's Athletic | Biscuit Factory Second XI v Causton's Athletic | 0.918 |
| 59 | Bromborough v Spital | Bromboro' v Spital | 0.919 |
| 18 | Reading v C.E. Keyser's XI | Reading v Keyser's XI | 0.93 |
| 34 | Colman Green v Gerrards Cross | Colham Green v Gerrards Cross | 0.931 |
| 9 | Dunstable First XI v Aston Clinton | Dunstable Town First XI v Aston Clinton | 0.932 |
| 53 | Lancashire Hill v Harpurhey Wesleyans | Lancashire-Hill SS v Harpurhey Wesleyans | 0.935 |
| 49 | Mr G H Ling's XI v Cheadle | G H Ling's XI v Cheadle | 0.936 |
| 51 | Macclesfield v Levenshulme | Macclesfield v Lever-Shulme | 0.943 |
| 7 | Hookliffe v Woburn | Hockliffe v Woburn | 0.944 |
| 57 | Chorlton A Team v Macclesfield Conservative Club | Chorlton A Team v Macclesfield Conservative | 0.945 |

## Surplus model rows on Willis-covered pages (review)

| Page | Matchup | Date | Type |
|---:|---|---|---|
| 4 | R H Haviland's XI v Luton Villa-Road | 18950803 | match information |
| 7 | Houghton v Westoning | 18950812 | match information |
| 8 | Luton Detachment v Remainder Of Third Vol Battalion | 18950810 | match information |
| 14 | All Saints' v Boys' Brigade (first Wokingham Company) Second XI | 18950518 | match information |
| 15 | Earley St Peter's | 18950500 | team information |
| 16 | Reading School player statistics | 18950715 | statistics |
| 16 | Reading School team aggregates | 18950715 | statistics |
| 17 | Biscuit Factory Second XI v White Cross | 18950727 | match information |
| 17 | Heath End v Mcilroy's | 18950801 | match information |
| 18 | Reading | 18950800 | newspaper cuttings |
| 18 | Reading v MCC | 18950805 | match information |
| 18 | Sunningdale School team aggregates | 18950800 | statistics |
| 19 | T W Girdlestone's XI team aggregates | 18950000 | statistics |
| 24 | Abingdon | 18950900 | team information |
| 24 | Abingdon team aggregates | 18950900 | statistics |
| 25 | Newbury team aggregates | 18950900 | statistics |
| 26 | Burghclere v Newtown | 18950900 | match information |
| 26 | Newtown team aggregates | 18950000 | statistics |
| 26 | Speen team aggregates | 18950000 | statistics |
| 26 | Stockcross team aggregates | 18950000 | statistics |
| 27 | 49th Regimental District team aggregates | 18950900 | statistics |
| 27 | Royal Berks Seed Establishment team aggregates | 18950900 | statistics |
| 29 | Lechlade | 18951031 | team information |
| 29 | Lechlade team aggregates | 18950000 | statistics |
| 30 | Maidenhead team aggregates | 18950000 | statistics |
| 32 | St John's | 18950719 | team information |
| 32 | Wycombe | 18950719 | newspaper cuttings |
| 33 | South Bucks | 18950803 | fixture information |
| 34 | Gerrards Cross v Osborne Stevens & Co | 18950731 | match information |
| 35 | Parish Church v Fenny Stratford St Martin | 18950803 | match information |
| 35 | Parish Church v Moulsoe | 18950805 | match information |
| 36 | Cippenham v Carlton London | 18950805 | match information |
| 39 | H Penton's XI v Hedgerley Home | 18950822 | match information |
| 40 | Hoare's XI v Haddenham | 18950727 | match information |
| 41 | Histon And Impington v Old Higher Grade | 18950727 | match information |
| 43 | K S Ranjitsinhji | 18950800 | biography |
| 48 | Garston v Liverpool Second XI | 18950706 | match information |
| 50 | Bollington v Heaton Mersey | 18950727 | match information |
| 50 | Brinksway Sunday School v Meadow | 18950727 | match information |
| 50 | Castleton and Stockport | 18950727 | newspaper cuttings |
| 50 | G H Ling's XI v Cheadle | 18950727 | match information |
| 50 | Lancashire Hill Sunday School v Haughton Wesleyans First XI | 18950727 | match information |
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
| 51 | Poynton v Great Moor | 18950810 | match information |
| 52 | Bollington Second XI v Bugsworth | 18950810 | match information |
| 52 | Phoenix v Marterers | 18950810 | match information |
| 52 | Stockport v Great Moor | 18950810 | match information |
| 54 | Port Sunlight v Helsby | 18950817 | match information |
| 54 | Woodland team aggregates | 18950000 | statistics |
| 55 | All Saints' | 18950800 | team information |
| 56 | St Thomas' Athletic | 18950831 | team information |
| 57 | Middlesex v Lancashire | 18950800 | match information |
| 57 | Phoenix Second XI v Moseley Second XI | 18950817 | match information |
| 57 | St Thomas' Athletic | 18950831 | team information |
| 58 | Birkenhead Victoria team aggregates | 18950900 | statistics |
| 58 | Formby team aggregates | 18950900 | statistics |
| 58 | Liverpool team aggregates | 18950900 | statistics |
| 58 | Northern team aggregates | 18950900 | statistics |
| 58 | Prescot team aggregates | 18950900 | statistics |
| 59 | Fixtures for To-Day | 18950914 | fixture information |
| 59 | Rock Ferry Second XI player statistics | 18950000 | statistics |
| 60 | Birkenhead Park team aggregates | 18950000 | statistics |
| 60 | Birkenhead Victoria team aggregates | 18950000 | statistics |
| 60 | Oxton team aggregates | 18950000 | statistics |
| 60 | Rock Ferry team aggregates | 18950000 | statistics |
| 61 | Birkenhead Park players | 18950900 | player information |
| 61 | Birkenhead Victoria players | 18950900 | player information |
| 61 | Birkenhead Victoria team aggregates | 18950900 | statistics |
| 61 | Bootle v Birkenhead Victoria | 18950907 | match information |
| 61 | Formby v New Brighton | 18950907 | match information |
| 61 | Liverpool v Oxton | 18950907 | match information |
| 61 | Oxton players | 18950900 | player information |
| 61 | Oxton team aggregates | 18950900 | statistics |
| 61 | Rock Ferry players | 18950900 | player information |
| 61 | Rock Ferry team aggregates | 18950900 | statistics |
| 61 | Rock Ferry v Cheadle Hulme | 18950907 | match information |
