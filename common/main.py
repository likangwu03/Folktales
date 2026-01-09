from common.utils.loader import load_json_folder, out_dir
from common.models.folktale import AnnotatedFolktale
from common.models.event import MIN_EVENTS
from common.utils.visualization import show_genre_distribution

def main():
	folktales_json = load_json_folder(out_dir)
	folktales = [AnnotatedFolktale(**folktale_json) for folktale_json in folktales_json.values()]
	
	for filename, folktale in zip(folktales_json.keys(), folktales):
		n_events = len(folktale.events)
		if n_events <= MIN_EVENTS:
			print(f"'{filename}' has too few events ({n_events}, minimum required: {MIN_EVENTS})")
	show_genre_distribution(folktales)

if __name__ == "__main__":
	main()