load("coeficientiInterpolare.mat")

% --- Generare caracteristica ---
x = 0:1:150;

y1 = x(1:inflexIndex+30)*p1(1) + p1(2);
y2 = x((inflexIndex+31):151)*p2(1) + p2(2);

y = [y1 y2];

% --- Domeniu ADC ---
ADC = 0:1:4095;

temp = zeros(size(ADC));

y_min = min(y);
y_max = max(y);

for i = 1:length(ADC)
    
    val = ADC(i);
    
    % --- Clamp ---
    if val <= y_min
        temp(i) = 150;   % maxim temperatura
        continue;
    elseif val >= y_max
        temp(i) = 0;     % minim temperatura
        continue;
    end
    
    % --- Cautare interval ---
    idx = find(y >= val, 1, 'last');
    
    % Punctele pentru interpolare
    x1 = x(idx);
    x2 = x(idx+1);
    
    y1 = y(idx);
    y2 = y(idx+1);
    
    % --- Interpolare liniara inversa ---
    temp(i) = x1 + (val - y1) * (x2 - x1) / (y2 - y1);
end

% --- Rotunjire ---
temp = round(temp, 2);

% --- Plot ---
figure;
plot(ADC, temp);
xlabel('ADC'); ylabel('Temperatura');
title('Conversie ADC -> Temperatura (cu cautare)');
grid on;

%salvare x 100
T = table(ADC(:), temp_round(:), 'VariableNames', {'ADC','Temperatura'});
writetable(T, 'adc_temp.csv');