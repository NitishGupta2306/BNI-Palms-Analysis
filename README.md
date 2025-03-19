# BNI-Palms-Analysis

### Deployment:
This program is currently deployed on https://bni-palms-analysis.onrender.com. There are still daily updates coming.

### Use case for this program:
##### This program generates a report for BNI usings PALMS data. It does the following:

1. Compiles as many palms report files as you give it.
2. Compiles the member names from a membership list
3. Generates two reports: refferal_matrix.xlsx and OTP_matrix.xlsx

---
### Generated Files:

##### refferal_matrix.xlsx:
1. This file contains a two-dimensional grid that tells you which memebers have recieved a referal from each given member.
2. The X-axis contains the reciving member's name (X-member).
3. The Y-axis contains the giving member's name (Y-member).
4. The remaining is a grid of numbers each representing the total numbers of referals given by Y-member to X-member.
5. The right-most columns shows the total referrals given and the total unique referrals given,
    - Unique referrals given = how many different members you have given a referral to.
6. the bottom-most rows show the total referrals recieved and the total unique referrals recieved.
    - Unique referrals recieved = how many different members have given you a referral to.


##### OTO_matrix.xlsx:
1. This file contains a two-dimensional grid that tells you which memebers have done a one to one with each other.
2. The X-axis and Y-axis contain member names.
3. The remaining is a grid of numbers each representing the total numbers of OTO between the members in the X and Y axis.
4. The right-most columns show the total OTOs conducted and the total unique OTOs conducted.
    - Unique OTOs = One to Ones performed with different members

##### combination_matrix.xlsx:
1. The X-axis and Y-axis contain member names.
2. This file contains a two-dimensional grid that tells you the combination of OTO and Referal values.
    - 0: implies that neither a OTO nor a referral has been passed between these members
    - 1: implies that a OTO has been done, but no referral has been passed.
    - 2: implies that a referral has been passed, but no OTO was done.
    - 3: implies that both a OTO was conducted and a referral was passed.
3. The right-most columns show the totals for each of the above mentioned types.

##### If you want to add any specific requests for this program, please add a git-issue or email me.