import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()
scores_file = open("programabull_scores.txt", 'w+')
scores_list = [(row[0], row[1]) for row in cursor.execute("SELECT username, score FROM user")]

print('{:<15}'.format("TEAM")+'{:>15}'.format("SCORE"), file=scores_file)
for user_score in sorted(scores_list, key=lambda x: x[1], reverse=True):
	print('{:<15}'.format(user_score[0]) + '{:>15}'.format(str(user_score[1])), file=scores_file)
