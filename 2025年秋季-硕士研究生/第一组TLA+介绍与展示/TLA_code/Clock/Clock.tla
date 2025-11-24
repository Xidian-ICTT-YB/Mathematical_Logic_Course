---- MODULE Clock ----
EXTENDS Integers, TLC

\* --algorithm DigitalClock
\*   variables hr = 12, min = 0;
\* begin
\*   while TRUE do
\*     if min < 59 then
\*       min := min + 1;
\*     else
\*       min := 0;
\*       if hr < 12 then
\*         hr := hr + 1;
\*       else
\*         hr := 1;
\*       end if;
\*     end if;
\*   end while;
\* end algorithm;

VARIABLES hr, min

\* 定义初始状态：时钟从 12:00 开始
Init == hr = 12 /\ min = 0

\* 定义一个动作：分钟向前走一格
Tick == /\ min' = min + 1
        /\ hr' = hr

\* 定义一个动作：分钟数达到59后，小时进位
WrapHour == /\ min' = 0
            /\ hr' = IF hr = 12 THEN 1 ELSE hr + 1

\* 定义下一步动作：要么是普通的 Tick，要么是小时进位
Next == \/ (min < 59 /\ Tick)
        \/ (min = 59 /\ WrapHour)

\* 定义完整的系统规约
Spec == Init /\ [][Next]_<<hr, min>>

\* 定义不变量：我们希望验证的属性
TypeOK == /\ hr \in 1..12
          /\ min \in 0..59

====