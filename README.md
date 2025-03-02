# BNI-Palms-Analysis

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

##### OTO_matrix.xlsx:
1. This file contains a two-dimensional grid that tells you which memebers have recieved a referal from each given member.
2. The X-axis and Y-axis contain member names.
3. The remaining is a grid of numbers each representing the total numbers of OTO between the members in the X and Y axis.

---
### Upcoming Features:
1. This program will soon be launched on docker to make it easier to run by any individual.
2. This program will let you enter files through an upload menu.

##### If you want to add any specific requests for this program, please add a git-issue or email me.