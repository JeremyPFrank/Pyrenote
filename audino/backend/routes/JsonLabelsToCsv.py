import json
import csv
from pprint import pprint
from backend import app


def test(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        text = JsonToRaven(data)
        print("===================================================")
        print(text)


def JsonToCsv(data, filename):
    with open(filename.replace(".json", ".csv"), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['filename', 'label', 'start', 'duration',
                             'max_freq', 'min_freq' 'created_at',
                             'last_modified', 'is_marked_for_review',
                             'assigned_users'])
        for audio in data:
            original_filename = audio['original_filename']
            assigned_users = audio['assigned_users']
            created_at = audio['created_at']
            filename = audio['filename']
            is_marked_for_review = audio['is_marked_for_review']
            # last_modified = audio['last_modified']
            segments = audio['segmentations']
            for region in segments:
                if len(region['annotations']) == 0:
                    label = "NO LABEL"
                else:
                    label = list(region['annotations'].values()
                                 )[0]['values']['value']
                last_modified = region['last_modified']
                end = region['end_time']
                start = region['start_time']
                max_freq = region['max_freq']
                min_freq = region['min_freq']
                spamwriter.writerow([original_filename, label, start,
                                     (end-start), max_freq, min_freq,
                                     created_at, last_modified,
                                     is_marked_for_review, assigned_users])


def JsonToText(data):
    text = ""
    csv = []
    text = write_row(text, ['IN FILE', 'CLIP LENGTH', 'OFFSET', 'DURATION',
                            'MAX FREQ', 'MIN FREQ', 'SAMPLE RATE', 'MANUAL ID'
                            'TIME_SPENT'])
    csv.append(['IN FILE', 'CLIP LENGTH', 'OFFSET', 'DURATION', 'MAX FREQ',
                'MIN FREQ', 'SAMPLE RATE', 'MANUAL ID', 'TIME_SPENT'])
    for audio in data:
        sampling_rate = audio['sampling_rate']
        clip_length = audio['clip_length']
        original_filename = audio['original_filename']
        segments = audio['segmentations']

        for region in segments:
            end = region['end_time']
            start = region['start_time']
            max_freq = region['max_freq']
            min_freq = region['min_freq']
            time_spent = region['time_spent']
            if len(region['annotations']) == 0:
                label = "NO LABEL"
                text = write_row(text, [original_filename, clip_length, start,
                                 round((end-start), 4),  max_freq, min_freq,
                                 sampling_rate, label,
                                 time_spent])
                csv.append([original_filename, clip_length, start,
                            round((end-start), 4),  max_freq, min_freq,
                            sampling_rate, label,
                            time_spent])
            else:
                for labelCate in region['annotations'].values():
                    print(labelCate)
                    values = labelCate["values"]
                    try:
                        for label in values:
                            print(label)
                            label = label['value']
                            text = write_row(text, [original_filename,
                                             clip_length, start,
                                             round((end-start), 4),
                                             max_freq, min_freq,
                                             sampling_rate, label,
                                             time_spent])
                            csv.append([original_filename, clip_length, start,
                                        round((end-start), 4),
                                        max_freq, min_freq,  sampling_rate,
                                        label, time_spent])
                    except Exception as e:
                        label = values['value']
                        text = write_row(text, [original_filename, clip_length,
                                                start, round((end-start), 4),
                                                max_freq, min_freq,
                                                sampling_rate, label,
                                                time_spent])
                        csv.append([original_filename, clip_length, start,
                                    round((end-start), 4), max_freq, min_freq,
                                    sampling_rate, label, time_spent])
    return text, csv


def JsonToRaven(data):
    text = ""
    text = write_row(text, ['Selection', 'View', 'Channel', 'Begin Time (s)',
                            'End Time (s)', 'Low Freq (Hz)',
                            'High Freq (Hz)', 'Species'], delimeter="	")
    audio = data
    segments = audio['segmentations']
    sampling_rate = round(audio['sampling_rate'] / 2)
    count = 1
    app.logger.info(sampling_rate)
    for region in segments:
        end = region['end_time']
        start = region['start_time']
        max_freq = region['max_freq']
        if (int(max_freq) < 0 or int(max_freq) > sampling_rate):
            max_freq = sampling_rate

        min_freq = region['min_freq']
        if (int(min_freq) < 0 or int(min_freq) > sampling_rate):
            min_freq = 0
        if len(region['annotations']) == 0:
            label = "NO LABEL"
            text = write_row(text, [count, 'Spectrogram 1', '1',
                                    start,  end, min_freq, max_freq, label],
                             delimeter="	")
        else:
            for labelCate in region['annotations'].values():
                print(labelCate)
                values = labelCate["values"]
                try:
                    for label in values:
                        print(label)
                        label = label['value']
                        text = write_row(text, [count, 'Spectrogram 1',
                                                '1', start,  end, min_freq,
                                                max_freq, label],
                                         delimeter="	")
                except Exception as e:
                    label = values['value']
                    text = write_row(text, [count, 'Spectrogram 1', '1',
                                     start,  end, min_freq, max_freq,
                                     label],
                                     delimeter="	")
                count += 1
    return text


def write_row(text, row, delimeter=","):
    for i in range(len(row)):
        text = text + str(row[i])
        if (i == (len(row) - 1)):
            text = text + "\n"
        else:
            text = text + delimeter
    return text
