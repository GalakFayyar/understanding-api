import requests
import csv
import time


def print_res_to_file(p_row, p_filename_entry, p_filename_result, p_redressage):
    entry_phrase, entry_quoi, entry_ou, entry_prox = p_row
    res = requests.get(url.format(phrase=entry_phrase, redressage=p_redressage))
    res = res.json()
    print("{phrase};{pattern};{result};{p1};{p2};{redressage};{filename}".format(
        phrase=res["analyse"]["phrase"],
        pattern=res["analyse"]["pattern"],
        result=True if (res["ou"] == entry_ou) and (res["quoi"] == entry_quoi) else False,
        p1=res["analyse"]["p1"],
        p2=res["analyse"]["p2"],
        redressage=p_redressage,
        filename=p_filename_entry), file=p_filename_result)


if __name__ == '__main__':
    filenames_entry = ["10k_top_monochamp.csv", "10k_hasard_monochamp_simple.csv", "10k_hasard_quiquoi_monochamp_simple.csv", "10k_hasard_ou_monochamp_simple.csv"]
    path_files = "./data_validation/{filename}"
    url = "http://localhost:9090/api-comprehension-1/quiquoiou?phrase={phrase}&redressage={redressage}&redis=False"
    t_start = time.time()

    enableRedressage = True
    nameOfFile = 'result_get_pattern_avec_redressage' if (enableRedressage) else 'result_get_pattern_sans_redressage'

    with open("./" + nameOfFile + ".csv", "a") as filename_result:
        print("phrase;pattern;result;p1;p2;redressage;filename", file=filename_result)
        for filename_entry in filenames_entry:
            with open(path_files.format(filename=filename_entry)) as entry:
                    reader = csv.reader(entry, delimiter=";", quotechar='"')
                    for row in reader:
                        if len(row) == 4:
                            print_res_to_file(row, filename_entry, filename_result, enableRedressage)
        t_end = time.time()
    print(t_end - t_start)
