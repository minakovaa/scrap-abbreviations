import os
from sentence_transformers import SentenceTransformer
from scipy import spatial
from collections import defaultdict
from scrap import save_abbreviation_to_json, load_abbreviations_from_json
from tqdm import tqdm


def compute_abbreviation_vectors(abbr_json, path_to_save_abbr_vec_json):
    abbr_descr = load_abbreviations_from_json(abbr_json)

    model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')  # ,cache_folder='sentence-transformer-model')

    abbr_embeddings = {abbr: model.encode(descr).tolist() for abbr, descr in abbr_descr.items()}

    save_abbreviation_to_json(abbr_embeddings, path_to_save_abbr_vec_json)

    return abbr_embeddings


def cosine_sim(vec_1, vec_2):
    """
    Compute cosine similarity between two 1-D vectors
    """
    return 1 - spatial.distance.cosine(vec_1, vec_2)


def find_sim_abbreviations(source_abbr_json: str, source_abbr_vec: str,
                           target_abbr_json: str, target_abbr_vec: str,
                           src_trg_abbr_output_json: str,
                           treshold_sim=0.7):
    """
    Find similar abbreviations in target abbreviations to source abbreviations.

    If 'source_abbr_vec' or 'target_abbr_vec' is not exist then the embeddings will computed.

    :param source_abbr_json: Path to json where abbreviations are keys and list of descriptions are values.
    :param source_abbr_vec: Path to json where abbreviations are keys and list of embeddings are values,
                            corresponding to 'source_abbr_json' file structure.
    :param target_abbr_json: Path to json where abbreviations are keys and list of descriptions are values.
    :param target_abbr_vec: Path to json where abbreviations are keys and list of embeddings are values,
                            corresponding to 'source_abbr_json' file structure.
    :param src_trg_abbr_output_json: Path to the output json with source-target abbreviation pairs.
    :param treshold_sim: Treshold from (0, 1) that break lower cosine similarity and
           must be selected by crossvalidation.
    :return: None
    """

    if os.path.exists(source_abbr_vec):
        source_abbr_embeddings = load_abbreviations_from_json(source_abbr_vec)
    else:
        print(f"Start to compute vector embedddins for source_abbr_json {source_abbr_json}")
        source_abbr_embeddings = compute_abbreviation_vectors(source_abbr_json, source_abbr_vec)  # evaluated 269 seconds
    print(f"Loaded source_abbr_vec from {source_abbr_vec}")

    if os.path.exists(target_abbr_vec):
        target_abbr_embeddings = load_abbreviations_from_json(target_abbr_vec)
    else:
        print(f"Start to compute vector embedddins for target_abbr_json {target_abbr_json}")
        target_abbr_embeddings = compute_abbreviation_vectors(target_abbr_json, target_abbr_vec)  # evaluated 1707 seconds
    print(f"Loaded target_abbr_vec from {target_abbr_vec}")

    src_trg_abbr = defaultdict(list)
    for src_abbr, list_of_src_vec in tqdm(source_abbr_embeddings.items()):
        for src_vec in list_of_src_vec:

            most_sim_candidate = None
            max_sim = 0
            for trg_abbr, list_of_trg_vec in target_abbr_embeddings.items():
                for num_desc, trg_vec in enumerate(list_of_trg_vec):
                    sim = cosine_sim(src_vec, trg_vec)

                    if sim > treshold_sim and max_sim < sim:
                        most_sim_candidate = trg_abbr  # (trg_abbr, num_desc) # if we want show description
                        max_sim = sim

            if most_sim_candidate:
                src_trg_abbr[src_abbr].append(most_sim_candidate)

    save_abbreviation_to_json(abbreviations=src_trg_abbr, json_filename=src_trg_abbr_output_json)


if __name__ == "__main__":
    bg_json_filename = "abbreviations/bg-abbr.json"
    bg_abbr_vec = "abbreviations/bg-abbr-vec.json"

    ru_json_filename = "abbreviations/ru-abbr.json"
    ru_abbr_vec = "abbreviations/ru-abbr-vec.json"

    ru_bg_abbr = "abbreviations/bg-ru-abbr.json"

    find_sim_abbreviations(source_abbr_json=bg_json_filename, source_abbr_vec=bg_abbr_vec,
                           target_abbr_json=ru_json_filename, target_abbr_vec=ru_abbr_vec,
                           src_trg_abbr_output_json=ru_bg_abbr)
