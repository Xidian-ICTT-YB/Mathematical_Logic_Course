检索网站：medline、scopus（检索式构建、订阅推送）、web of science、cnki、cnki翻译助手（查找同义词）、pubmed、**endnote**

检索案例：消费者正面评价归因
- **将检索内容分解为词汇，找英文同类表达**
- 分解为：消费者+正面评价，去掉归因（由于“归因”是比较书面化的“原因”，可以暂时去掉“归因”）
- consumer* AND positive evaluation，可以搜索到8篇
- medline/endnote
- 加入归因后，无法搜索到结果


检索技能小结：
- 拆分目标，同义词替换，排列组合
- 拆分后的单词进行A **and** B **and** C 形式进行检索，其中A为a1 **or** a2 **or** a3（a1、a2、a3为同义词） 形式，B、C同理
- 重复上述操作，得到最优检索式

检索案例：二氧化碳还原检索式构建
- 百度搜索，确定同义专有名词，确定体系（光、电还原）（化学还原，催化还原）
- 标题、检索 (CO2 OR "carbon dioxide") AND (electro reduction OR "electrochemical reduction" OR "electrocatalytic reduction")   pubmed/medline
- 前五篇，或者按照时间降序排序，前5篇都相关则说明检索式不必优化了

检索案例：物流需求预测
- web of science 高级检索
- TI=(logistic*) AND TI=(demand* OR requirement*) AND TI=(forecast* OR predict*)
- 上式：搜索的论文title中同时包含物流、需求、预测，*是通配符
- 对于一些不相关的词汇，可以用not排除


使用sat/smt解决并发程序的问题  Using sat / smt to solve the problem of concurrent program
- 拆分目标，同义词替换，排列组合
**拆分单词**
- 并发程序concurrent program
- SAT：Boolean Satisfiability Problem/布尔公式可满足性问题
	- 布尔公式+可满足性（问题）
- SMT：satisfiability modulo theories/可满足性模理论
	- 模理论+可满足性
- 解决：solutions
- 问题：problems


**同义词替换**
- 并发程序：concurrent program / multi-threaded programs
- 布尔公式：boolean formula
- 可满足性：satisfiability / satisfiable
- 模理论：modulus theory
- 解决：solution /  treatment
- 问题：problem / fault
web of science检索
((TS=(SAT* OR SMT*)) AND (TS=(concurrent program* OR multi-threaded program*)) AND (TS=modulus theory*) AND (TS=boolean formula*) AND (TS=(problem* OR fault*)) AND (TS=(solution* OR treatment*)))
**重复、偏理论、目标论文是应用**
2.((TS=(SAT* OR SMT*)) AND (TS=(concurrent program* OR multi-threaded program*)) AND (TS=(problem* OR fault*)) AND (TS=(solution* OR treatment*)))
**无关信息放入摘要里**
2.((TS=(SAT* OR SMT*)) AND (TS=(concurrent program* OR multi-threaded program*)) AND (AB=(problem* OR fault*)) AND (AB=(solution* OR treatment*)))
**直接删除次要信息**
3.((TS=(SAT* OR SMT*)) AND (TS=(concurrent program* OR multi-threaded program*)))

medline检索：
((SAT* OR SMT*) AND (concurrent program* OR multi-threaded program*))













((TS=(SAT* OR SMT*)) AND (TS=(concurrent program* OR multi-threaded program*)) AND (TS=(problem* OR fault*)) AND (TS=(solution* OR treatment*)))