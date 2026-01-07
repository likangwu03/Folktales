from common.utils.loader import load_json_folder, out_dir
from common.models.folktale import AnnotatedFolktale
from common.models.event import MIN_EVENTS
from annotation.visualization import show_genre_distribution

def main():
	folktales_json = load_json_folder(f"{out_dir}/annotated")
	folktales = [AnnotatedFolktale(**folktale_json) for folktale_json in folktales_json.values()]
	
	for filename, folktale in zip(folktales_json.keys(), folktales):
		n_events = len(folktale.events)
		if n_events <= MIN_EVENTS:
			print(filename)

	show_genre_distribution(folktales)

if __name__ == "__main__":
	main()