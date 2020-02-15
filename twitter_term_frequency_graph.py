# Chap02-03/twitter_term_frequency_graph.py 
y = [count for tag, count in tf.most_common(30)]
x = range(1, len(y)+1)
plt.bar(x, y)
plt.title("Term Frequencies")
plt.ylabel("Frequency")
plt.savefig('term_distribution.png')