
SQL_JOURNAL_TOTAL_ENGAGEMENT = """
    SELECT 
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    GROUP BY 
        journal.journal_id, journal.journal
    ORDER BY 
        total_interactions DESC;
           
"""

# journal_id	journal	total_reads	total_downloads	total_interactions   	
# 2	The Lamp	533	79	612	
# 1	The Gavel	260	56	316	
# 3	The Star	66	12	78	
# 9	Example1	0	0	0	


SQL_JOURNAL_MONTHLY_ENGAGEMENT= """
  SELECT 
        journal.journal_id,
        journal.journal,
        MONTH(logs.date) AS month,
        COUNT(CASE WHEN logs.type = 'read' THEN logs.article_id END) AS monthly_reads,
        COUNT(CASE WHEN logs.type = 'download' THEN logs.article_id END) AS monthly_downloads
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    WHERE
        logs.type IN ('read', 'download')
    GROUP BY 
        journal.journal_id, journal.journal, month
    ORDER BY 
        month, journal.journal_id;

"""

# journal_id	journal	month   	monthly_reads	monthly_downloads	
# 2	The Lamp	10	4	0	
# 3	The Star	10	1	0	
# 1	The Gavel	11	247	56	
# 2	The Lamp	11	360	75	
# 3	The Star	11	50	12	
# 1	The Gavel	12	13	0	
# 2	The Lamp	12	169	4	
# 3	The Star	12	15	0	


SQL_MOST_POPULAR_ARTICLES =   """
    SELECT 
  		logs.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    GROUP BY 
        journal.journal_id, journal.journal,article.article_id
    ORDER BY 
        total_interactions DESC
    LIMIT 10;
"""

# article_id	title	journal_id	journal	total_reads	total_downloads	total_interactions   	
# 10	A Classroom-based Action Research on Selected Firs...	2	The Lamp	276	43	319	
# 825	Impact of Part-time Job on Academic Performance of...	2	The Lamp	184	14	198	
# 814	Research on Selected First Year Infor- mation Tech...	1	The Gavel	139	29	168	

SQL_MOST_DOWNLOADED_ARTICLES =   """
    SELECT 
  		logs.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    GROUP BY 
        journal.journal_id, journal.journal,article.article_id
    ORDER BY 
        total_downloads DESC
    LIMIT 10;
"""

SQL_MOST_VIEWED_ARTICLES =   """
    SELECT 
  		logs.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    GROUP BY 
        journal.journal_id, journal.journal,article.article_id
    ORDER BY 
        total_reads DESC
    LIMIT 10;
"""


SQL_MOST_POPULAR_ARTICLES_GAVEL = """
    SELECT 
  		logs.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    WHERE 
    	journal.journal_id = 1
    GROUP BY 
        journal.journal_id, journal.journal,article.article_id
    ORDER BY 
        total_interactions DESC
    LIMIT 10;
"""
SQL_MOST_POPULAR_ARTICLES_LAMP = """
    SELECT 
  		logs.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    WHERE 
    	journal.journal_id = 2
    GROUP BY 
        journal.journal_id, journal.journal,article.article_id
    ORDER BY 
        total_interactions DESC
    LIMIT 10;
"""

SQL_MOST_POPULAR_ARTICLES_STAR = """
    SELECT 
  		logs.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS total_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS total_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    WHERE 
    	journal.journal_id = 3
    GROUP BY 
        journal.journal_id, journal.journal,article.article_id
    ORDER BY 
        total_interactions DESC
    LIMIT 10;
"""


SQL_AUTHOR_ARTICLE_INTERACTIONS = """
    SELECT 
        article.author_id,
        article.article_id,
        article.title,
        journal.journal_id,
        journal.journal,
        MONTH(logs.date) AS view_month,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS monthly_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS monthly_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    LEFT JOIN 
        logs ON article.article_id = logs.article_id
    WHERE
        article.author_id = 2
    GROUP BY 
        journal.journal_id, journal.journal, logs.article_id, view_month
    ORDER BY 
        total_interactions DESC, view_month, article.article_id;

"""

# author_id	article_id	title	journal_id	journal	view_month   	monthly_reads	monthly_downloads	total_interactions   	
# 2	3	Addressing The Trade Offs Between Labor Productivi...	1	The Gavel	11	44	12	56	
# 2	5	The Effectiveness of Electronic Wallet as alternat...	1	The Gavel	11	17	1	18	
# 2	3	Addressing The Trade Offs Between Labor Productivi...	1	The Gavel	12	7	0	7	
# 2	4	The Effects of Social Isolation, Remote Work Satis...	1	The Gavel	11	5	0	5	
# 2	26	School Leaders' Crisis Leadership Competencies And...	2	The Lamp	NULL	0	0	0	
input=""
SQL_AUTHOR_MONTHLY_INTERACTIONS = f"""
    SELECT 
        article.author_id,
        MONTH(logs.date) AS month,
        SUM(CASE WHEN logs.type = 'read' THEN 1 ELSE 0 END) AS monthly_reads,
        SUM(CASE WHEN logs.type = 'download' THEN 1 ELSE 0 END) AS monthly_downloads,
        COUNT(logs.article_id) AS total_interactions
    FROM 
        journal
    LEFT JOIN 
        article ON journal.journal_id = article.journal_id
    RIGHT JOIN 
        logs ON article.article_id = logs.article_id
    WHERE
        article.author_id = {input}
    GROUP BY 
        month
    ORDER BY 
        total_interactions DESC, month;

"""

# author_id 	month Ascending 2 	monthly_reads 	monthly_downloads 	total_interactions Descending 1 	
# 2 	11 	66 	13 	79
# 2 	12 	7 	0 	7



def execute_query(query, connection):
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    return result
