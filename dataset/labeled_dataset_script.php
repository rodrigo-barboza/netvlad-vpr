<?php

function classes_range(): array
{
    return [
        'bancadas_a' => [
            [0, 186],
            [651, 836],
        ],
        'bancadas_b' => [
            [187, 481],
            [876, 1271],
        ],
        'corredor' => [
            [191, 206],
            [456, 876],
            [831, 876],
            [1246, 1346],
        ],
        'armarios' => [
            [1351, 1746],
            [2216, 2291],
        ],
        'porta' => [
            [1751, 2211],
        ],
    ];
}

function resolve_image_class(string $image): string
{
    $file_number = (int) substr($image, 5, 5);

    foreach(classes_range() as $class => $ranges) {
        foreach($ranges as [$min, $max]) {
            if (($file_number >= $min && $file_number <= $max)) {
                $resolved_class = $class;
                break;
            }
        }
    }

    return $resolved_class;
}

function read_directory(): void
{
    $content = scandir('./');

    $content = array_diff($content, ['.', '..']);

    $csv_content = '';
    foreach($content as $file) {
        if (str_contains($file, 'frame')) {
            $csv_content .= "$file;" . resolve_image_class($file) . ";\r\n";
        }
    }

    file_put_contents('labeled_dataset.csv', $csv_content);
}

read_directory();
