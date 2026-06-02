\# Sample Outputs



\## Search Request



Input:



Part Number: PART1001

Home Site  : SITE\_A





\## Sample Result



| Site   |   APN    | Units| Status   | Distance |

|--------|----------|------|----------|----------|

| SITE\_B | PART1001 |   12 | Above Min|   14.2   |

| SITE\_C | PART1001 |   4  | At Min   |   27.8   |

| SITE\_D | PART1001 |   8  | Above Min|   41.3   |





\## Slack Command



@PART\_FINDER PART1001 SITE\_A



\---



\## Slack Response



SITE      APN       UNITS    STATUS      DIST

\----------------------------------------------

SITE\_B    PART1001  12       Above Min   14.2

SITE\_C    PART1001  4        At Min      27.8

SITE\_D    PART1001  8        Above Min   41.3

