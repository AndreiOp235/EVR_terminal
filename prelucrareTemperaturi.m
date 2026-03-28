load('temperaturi.mat');

% Funcția care elimină maxim 12 outliers dintr-un vector
eliminaOutliers = @(v) eliminaMax12Outliers(v);

% Aplicăm funcția pentru fiecare set de 100 de iteratii
temperaturi = cellfun(@(cellIteratii) ...
    cellfun(eliminaOutliers, cellIteratii, 'UniformOutput', false), ...
    temperaturi, 'UniformOutput', false);


%% calculam o medie noua per temperatura
iter=zeros(100,1);
mediiTemp=zeros(81,1);
for temperatura=1:81
    for iteratie=1:100
        iter(iteratie)=mean(mean(temperaturi{temperatura}{iteratie},'omitnan'));
    end
    mediiTemp(temperatura)=mean(iter);
end

%% date masurate
x = 30:1:110;
plot(x, mediiTemp, 'b', 'LineWidth', 2);
hold on;

% parametri
R0 = 10000;
T0 = 25 + 273.15;
B  = 3950;
Rfix = 10000;

Vcc = 5;     % sau 5.0
Vd  = 0;     % cadere dioda

% calcul
T = x + 273.15;
Rntc = R0 .* exp(B .* (1./T - 1./T0));

ADC_ideal = 4095 .* (Rntc ./ (Rfix + Rntc)) .* ((Vcc - Vd)/Vcc);

% plot
plot(x, ADC_ideal+700, 'r--', 'LineWidth', 2);

title('ADC masurat vs ideal');
xlabel('Temperatura (°C)');
ylabel('ADC');
legend('Masurat', 'Ideal');
grid on;

%% intepolare
% --- Datele punctelor ---
xData = 30:1:110;        % coordonatele x
yData = mediiTemp;       % coordonatele y (vector existent)

% --- Punctul de inflexiune ---
% Poate fi ales fie ca index, fie ca valoare x
inflexIndex = 50;  % exemplu: al 40-lea punct din vector

% --- Segmentele ---
x1 = xData(1:inflexIndex);
y1 = yData(1:inflexIndex);

x2 = xData(inflexIndex:end);
y2 = yData(inflexIndex:end);

% --- Interpolarea liniara pe fiecare segment ---
p1 = polyfit(x1, y1, 1);  % coeficienti linie 1
p2 = polyfit(x2, y2, 1);  % coeficienti linie 2

% --- Generare valori pentru plot ---
xx1 = linspace(x1(1), x1(end), 100);
yy1 = polyval(p1, xx1);

xx2 = linspace(x2(1), x2(end), 100);
yy2 = polyval(p2, xx2);

% --- Plot ---
figure;
plot(xData, yData, 'ko-', 'MarkerFaceColor','k'); hold on; % puncte originale
plot(xx1, yy1, 'b-', 'LineWidth', 2);                      % linia segment 1
plot(xx2, yy2, 'r-', 'LineWidth', 2);                      % linia segment 2
plot(xData(inflexIndex), yData(inflexIndex), 'go', 'MarkerSize', 10, 'MarkerFaceColor','g'); % punct inflexiune
legend('Date originale','Segment 1','Segment 2','Punct inflexiune');
xlabel('x'); ylabel('y');
title('Interpolare prin 2 drepte cu punct de inflexiune');
grid on;


%% --- Setare date ---
xData = 30:1:110;        % coordonatele x
yData = mediiTemp(:)';    % asiguram vector linie

% Verificam compatibilitatea lungimilor
if length(xData) ~= length(yData)
    error('xData si mediiTemp trebuie sa aiba aceeasi lungime!');
end

% --- Punctul de inflexiune ---
inflexIndex = 50;  % indexul punctului de inflexiune
if inflexIndex < 2 || inflexIndex > length(xData)-1
    error('inflexIndex trebuie sa fie intre 2 si length(xData)-1');
end

% --- Segmente ---
x1 = xData(1:inflexIndex);
y1 = yData(1:inflexIndex);

x2 = xData(inflexIndex:end);
y2 = yData(inflexIndex:end);

% --- Interpolare liniara ---
p1 = polyfit(x1, y1, 1);  
p2 = polyfit(x2, y2, 1);  

xx1 = linspace(x1(1), x1(end), 100);
yy1 = polyval(p1, xx1);

xx2 = linspace(x2(1), x2(end), 100);
yy2 = polyval(p2, xx2);

% --- Calcul abatere punct cu punct ---
abatere = zeros(size(yData));

% Segment 1
y_fit1 = polyval(p1, x1);
abatere(1:inflexIndex) = y1 - y_fit1;

% Segment 2
y_fit2 = polyval(p2, x2);
abatere(inflexIndex:end) = y2 - y_fit2;

% --- Plot interpolare ---
figure;
plot(xData, yData, 'ko-', 'MarkerFaceColor','k'); hold on;
plot(xx1, yy1, 'b-', 'LineWidth', 2);
plot(xx2, yy2, 'r-', 'LineWidth', 2);
plot(xData(inflexIndex), yData(inflexIndex), 'go', 'MarkerSize', 10, 'MarkerFaceColor','g');
legend('Date originale','Segment 1','Segment 2','Punct inflexiune');
xlabel('x'); ylabel('y');
title('Interpolare prin 2 drepte cu punct de inflexiune');
grid on;

% --- Calcul eroare procentuala ---
eroare_proc = abs(abatere) ./ abs(yData) * 100;

% --- Plot eroare procentuala ---
figure;
plot(xData, eroare_proc, 'mo-', 'MarkerFaceColor','m');
xlabel('x'); ylabel('Eroare [%]');
title('Eroarea procentuala fata de cele 2 drepte');
grid on;

% --- Eroarea procentuala RMS ---
rms_eroare_proc = sqrt(mean(eroare_proc.^2));
disp(['Eroarea procentuala RMS fata de interpolare: ', num2str(rms_eroare_proc), '%']);