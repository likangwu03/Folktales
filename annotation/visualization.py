import matplotlib.pyplot as plt
from common.models.folktale import GenreClass, AnnotatedFolktale
from collections import Counter
from common.utils.loader import save_fig
from loguru import logger

def show_genre_distribution(folktales: list[AnnotatedFolktale]):
	labels = [genre.value for genre in GenreClass]
	
	genre_counts = Counter(folktale.has_genre for folktale in folktales)
	
	total = sum(genre_counts.values())

	percentages = [
		(genre_counts[genre] / total) * 100 if total > 0 else 0
		for genre in GenreClass
	]

	fig = plt.figure(figsize=(8, 6))
	plt.bar(labels, percentages)
	plt.ylabel("Percentage (%)")
	plt.title("Genre Distribution (Normalized)")
	plt.xticks(rotation=30)
	plt.tight_layout()
	filename = "genre_distribution.png"
	save_fig(fig, filename)
	# plt.show()

	logger.debug(f"Genre distribution plot saved as {filename}.")