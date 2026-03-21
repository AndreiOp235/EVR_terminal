clc;
clear;
%close all;

folderPath = 'CSV';
files = dir(fullfile(folderPath, 'frame_*.csv'));
numFiles = length(files);

if numFiles == 0
    error('Nu s-au găsit fișiere CSV.');
end

% Matrice 3D: 8x8xN
allData = zeros(8,8,numFiles);
for k = 1:numFiles
    filePath = fullfile(folderPath, files(k).name);
    data = readmatrix(filePath);
    allData(:,:,k) = data;
end

% Media pe fiecare termistor
meanData = mean(allData, 3);

% ===== Heatmap =====
figure;
imagesc(meanData);
colorbar;

% --- FIXARE RANGE 0-4000 ---
clim([0 4000]); % Pentru MATLAB R2022a sau mai nou
% caxis([0 4000]); % Folosește asta dacă ai o versiune mai veche

axis equal tight;
set(gca,'YDir','normal');
title('Media valorilor termistorilor (0 - 4000)');
xlabel('Termistor P1');
ylabel('Bank');
colormap jet;

% ===== Scriere valori peste heatmap =====
for i = 1:8
    for j = 1:8
        val = meanData(i,j);
        
        % Dinamism pentru contrast: dacă valoarea e mare (fundal deschis), 
        % scriem cu negru, altfel cu alb.
        textColor = 'white';
        if val > 2500
            textColor = 'black';
        end
        
        text(j, i, sprintf('%.0f', val), ...
            'HorizontalAlignment', 'center', ...
            'Color', textColor, ...
            'FontSize', 9, ...
            'FontWeight','bold');
    end
end