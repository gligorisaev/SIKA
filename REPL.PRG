SELECT 1
USE povrat
SELECT 2
USE naslov INDEX naslov
SELECT 3
USE magdok INDEX inmagdok
SELECT 1
GO TOP
DO WHILE !EOF()
   m_slog=SUBSTR(tip_dok,1,1)+STRZERO(mag,3)+SUBSTR(br_dok,1,6)
   SELECT 2
   SEEK m_slog
   IF FOUND()
      DO WHILE !EOF() .AND. m_slog=SUBSTR(tip_dok,1,1)+STRZERO(mag,3)+SUBSTR(br_dok,1,6)
         REPLACE td WITH '3', oznaka WITH ' '
         SKIP
      END DO
   END IF
   SELECT 3
   SEEK m_slog
   IF FOUND()
      DO WHILE !EOF() .AND. m_slog=SUBSTR(tip_dok,1,1)+STRZERO(mag,3)+SUBSTR(br_dok,1,6)
         REPLACE td WITH '3'
         SKIP
      END DO
   END IF
   SELECT 1
   SKIP
END DO
QUIT