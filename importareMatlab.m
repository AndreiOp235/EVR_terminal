%% Setări folder
numeFolderRadacina = 'CSV-uri'; 

% 1. Obținem lista de fișiere
listaFisiere = dir(fullfile(numeFolderRadacina, '**', '*.csv'));
listaFisiere = listaFisiere(~[listaFisiere.isdir]);

% 2. SORTARE NUMERICĂ MANUALĂ (Robustă)
T_lista = struct2table(listaFisiere);

% Extragem numărul din folder (ex: din 'TEMP_95' extragem 95)
% Folosim regexp pentru a găsi cifrele din calea folderului
folderPaths = T_lista.folder;
numereFolder = zeros(height(T_lista), 1);

for k = 1:height(T_lista)
    % Căutăm ultima secvență de cifre din calea folderului
    tokens = regexp(folderPaths{k}, '(?<=TEMP_)\d+', 'match');
    if ~isempty(tokens)
        numereFolder(k) = str2double(tokens{end});
    end
end

% Extragem numărul din numele fișierului (ex: din 'iteratie_001.csv' extragem 1)
numeFisiere = T_lista.name;
numereFisier = zeros(height(T_lista), 1);

for k = 1:height(T_lista)
    tokens = regexp(numeFisiere{k}, '\d+', 'match');
    if ~isempty(tokens)
        numereFisier(k) = str2double(tokens{1});
    end
end

% Adăugăm coloanele numerice în tabel pentru sortare
T_lista.idxFolder = numereFolder;
T_lista.idxFisier = numereFisier;

% Sortăm tabelul pur numeric (metodă suportată de toate versiunile)
T_lista = sortrows(T_lista, {'idxFolder', 'idxFisier'});

% Convertim înapoi în structură
listaFisiere = table2struct(T_lista);

fprintf('Am găsit %d fișiere sortate numeric (TEMP_69 -> TEMP_110). Începe importul...\n', height(T_lista));

%% 3. Importul datelor (textscan)
numarFisiere = numel(listaFisiere);
dateCelule = cell(numarFisiere, 1);
formatSpec = '%s%f%f%f%f%f%f%f%f';

for i = 1:numarFisiere
    caleCompleta = fullfile(listaFisiere(i).folder, listaFisiere(i).name);
    
    fid = fopen(caleCompleta, 'rt');
    if fid == -1, continue; end
    
    try
        fgetl(fid); % Sărim header
        dateRaw = textscan(fid, formatSpec, 'Delimiter', ',');
        fclose(fid);
        
        % Construim tabelul
        % Convertim manual celula din textscan în string/tabel
        T = table(string(dateRaw{1}), dateRaw{2}, dateRaw{3}, dateRaw{4}, ...
                  dateRaw{5}, dateRaw{6}, dateRaw{7}, dateRaw{8}, dateRaw{9}, ...
                  'VariableNames', {'Bank', 'P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'});
        
        [~, numeFolder] = fileparts(listaFisiere(i).folder);
        T.SursaFolder = repmat(string(numeFolder), height(T), 1);
        T.NumeFisier = repmat(string(listaFisiere(i).name), height(T), 1);
        
        dateCelule{i} = T;
    catch
        if fid ~= -1, fclose(fid); end
    end
end

% Unire și Salvare
dateCelule = dateCelule(~cellfun(@isempty, dateCelule));
dataMare = vertcat(dateCelule{:});
save('date_importate.mat', 'dataMare', '-v7.3');
disp('--- IMPORT FINALIZAT CU SUCCES ---');