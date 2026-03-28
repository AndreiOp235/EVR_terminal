% --- Funcția auxiliară ---
function v = eliminaMax12Outliers(v)
    % Înlocuiește valorile 0 cu NaN
    v(v == 0) = NaN;

    % Media ignorând NaN
    m = mean(v, 'omitnan');

    % Distanța față de medie
    dist = abs(v - m);

    % Indexăm doar valorile valide
    validIdx = ~isnan(dist);

    % Sortează descrescător distanța față de medie
    [~, sortIdx] = sort(dist(validIdx), 'descend');

    % Eliminăm maxim 12 valori
    numToRemove = min(8, length(sortIdx));
    removeIdx = find(validIdx);
    removeIdx = removeIdx(sortIdx(1:numToRemove));

    v(removeIdx) = NaN;
end