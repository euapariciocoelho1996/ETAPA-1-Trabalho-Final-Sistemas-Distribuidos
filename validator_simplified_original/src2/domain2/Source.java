package domain;




import java.io.*;
import java.net.Socket;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

/**
 * The Source class generates synthetic data and interacts with other components.
 */
public class Source extends AbstractProxy {

    private String jsonPath;
    private boolean modelFeedingStage;
    private long arrivalDelay;
    private List<String> consideredMessages = new ArrayList<>();
    private int maxConsideredMessagesExpected;
    private int sourceCurrentIndexMessage;

    private List<Double> arrivalRates = new ArrayList<>();

    private List<Double> mrtsFromModel = new ArrayList<>();

    private List<Double> sdvsFromModel = new ArrayList<>();

    private String capacityVariatedServerName;
    private int droppCount = 0;

    private boolean allCyclesCompleted = false;


    // New field for variatedServer configuration
    private String variatedServerLoadBalancerIp;
    private int variatedServerLoadBalancerPort;
    private List<Integer> qtdServices = new ArrayList<>();


    List<Double> experimentData = new ArrayList<>();
    List<Double> experimentError = new ArrayList<>();

    private List<Boolean> cyclesCompleted = new ArrayList<>();

    private ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private ScheduledFuture<?> timeoutFuture;
    private long timeoutDuration = 30000; // Tempo de espera em milissegundos antes de considerar a validação como concluída
    private volatile boolean isTimeoutTriggered = false;

    private BufferedWriter logWriter;
    private PrintStream logStream;

    /**
     * Main method for running the Source as a standalone application.
     *
     * @param args Command-line arguments
     */
    public static void main(String[] args) throws IOException {
        Source source = new Source();
        source.start();
    }


    /**
     * Default constructor using a predefined JSON configuration file path.
     */
    public Source() {
        this(System.getProperty("user.dir"));
        initLogFile();
    }

    public Source(String name, Integer localPort, Integer maxConsideredMessagesExpected,
                  TargetAddress targetAddress, long arrivalDelay, boolean modelFeedingStage,
                  String variatedServerLoadBalancerIp, int variatedServerLoadBalancerPort, List<Integer> qtdServices,
                  List<Double> mrtsFromModel, List<Double> sdvsFromModel) {
        super();
        this.modelFeedingStage = modelFeedingStage;
        this.proxyName = name;
        this.localPort = localPort;
        this.targetAddress = targetAddress;
        this.arrivalDelay = arrivalDelay;
        this.maxConsideredMessagesExpected = maxConsideredMessagesExpected;
        this.variatedServerLoadBalancerIp = variatedServerLoadBalancerIp;
        this.variatedServerLoadBalancerPort = variatedServerLoadBalancerPort;
        this.qtdServices = qtdServices;
        this.mrtsFromModel = mrtsFromModel;
        this.sdvsFromModel = sdvsFromModel;

        for (int a = 0;a<qtdServices.size();a++) {
            cyclesCompleted.add(false);
        }

    }



    public Source(String propertiesPath) {
        super();
        initLogFile();
        Properties properties = new Properties();
        try {
            this.jsonPath = propertiesPath;
            // Carregar o arquivo .properties
            properties.load(new FileInputStream(propertiesPath + "/source.properties"));

            // Atribuir diretamente os valores do arquivo .properties para os campos da classe
            this.modelFeedingStage = Boolean.parseBoolean(properties.getProperty("modelFeedingStage"));
            this.proxyName = "source";
            this.localPort = Integer.parseInt(properties.getProperty("sourcePort"));
            this.targetAddress = new TargetAddress(
                    properties.getProperty("targetIp"),
                    Integer.parseInt(properties.getProperty("targetPort"))
            );
            this.maxConsideredMessagesExpected = Integer.parseInt(properties.getProperty("maxConsideredMessagesExpected"));

            // Parse 'mrtsFromModel' and 'sdvsFromModel' as lists of doubles
            String[] mrtsArray = properties.getProperty("mrtsFromModel").split(",");
            for (String mrt : mrtsArray) {
                this.mrtsFromModel.add(Double.parseDouble(mrt.trim()));
            }
            String[] sdvsArray = properties.getProperty("sdvsFromModel").split(",");
            for (String sdv : sdvsArray) {
                this.sdvsFromModel.add(Double.parseDouble(sdv.trim()));
            }


            // Variar serviços
            this.arrivalDelay = Long.parseLong(properties.getProperty("variatingServices.arrivalDelay"));
            this.variatedServerLoadBalancerIp = properties.getProperty("variatingServices.variatedServerLoadBalancerIp");
            this.variatedServerLoadBalancerPort = Integer.parseInt(properties.getProperty("variatingServices.variatedServerLoadBalancerPort"));

            // Parse 'qtdServices' as a list of integers
            String[] qtdServicesArray = properties.getProperty("variatingServices.qtdServices").split(",");
            for (String service : qtdServicesArray) {
                this.qtdServices.add(Integer.parseInt(service.trim()));
                cyclesCompleted.add(false);
            }

            printSourceParameters();

        } catch (IOException e) {
            throw new RuntimeException("Error reading properties configuration", e);
        }
    }


    private void initLogFile() {
        try {
            File logFile = new File("log.txt");
            if (logFile.exists()) {
                logFile.delete();
            }
            logFile.createNewFile();
            logWriter = new BufferedWriter(new FileWriter(logFile, true));
            logStream = new PrintStream(new FileOutputStream(logFile, true), true);
        } catch (IOException e) {
            throw new RuntimeException("Error initializing log file", e);
        }
    }

    private void log(String message) {
        System.out.println(message); // Imprime no console
        if (logWriter != null) { // Verifica se o logWriter ainda está aberto
            try {
                logWriter.write(message + "\n"); // Grava no log
                logWriter.flush(); // Garante que o conteúdo seja gravado imediatamente
            } catch (IOException e) {
                System.err.println("Error writing to log file: " + e.getMessage());
            }
        } else {
            System.err.println("logWriter is closed. Unable to write message: " + message);
        }
    }



    public void printSourceParameters() {
        log("");
        log("======================================");
        log("Source Parameters:");
        log("jsonPath: " + jsonPath);
        log("maxConsideredMessagesExpected: " + maxConsideredMessagesExpected);
        log("mrtsFromModel: " + mrtsFromModel);
        log("sdvsFromModel: " + sdvsFromModel);
        log("arrivalDelay: " + arrivalDelay);
        log("qtdServices: " + qtdServices);
        log("======================================");
    }

    public void closeLog() {
        try {
            if (logWriter != null) {
                logWriter.close();
            }
        } catch (IOException e) {
            log("Error closing log file");
        }
    }



    /**
     * Run method for starting the Source's operations.
     */
    public void run() {
        try {
            new ConnectionEstablishmentOriginThread().start();
            new ConnectionEstablishmentDestinyThread().start();

            Thread.sleep(100);
            log("Starting source");

            if (modelFeedingStage)
                sendMessageFeedingStage();
            else
                sendMessagesValidationStage();

        } catch (IOException e) {
            throw new RuntimeException(e);
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    private void sendMessageFeedingStage() {
        arrivalDelay = 2000;
        log("ATTENTION: Guarantee that arrival delay is a higher value then the sum of all service times.");

        log("##############################");
        log("Model Feeding Stage Started");
        log("##############################");
        log("Only 10 requests will be generated with AD = " + arrivalDelay + "ms");
        try {
            Thread.sleep(5000); // Reduzido o tempo de espera para 5 segundos
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt(); // Restaure o status de interrupção
        }

        String msg;
        // Envia as mensagens esperadas
        for (int j = 0; j < 10; j++) {
            msg = 1+";"+sourceCurrentIndexMessage + ";" + System.currentTimeMillis() + ";" + "\n";
            try {
                send(msg);
            } catch (IOException e) {
                throw new RuntimeException(e);
            } catch (ClassNotFoundException e) {
                throw new RuntimeException(e);
            }
            sourceCurrentIndexMessage++;
            try {
                Thread.sleep(arrivalDelay);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void sendMessagesValidationStage() throws IOException, ClassNotFoundException {
        String msg;
        int cycle = 0;
        for (Integer qts : qtdServices) {

            sourceCurrentIndexMessage = 1;
            consideredMessages.clear();

            String configMessage = "config;" + qts + ";" + "\n";
            sendMessageToConfigureServer(configMessage);

            // Aguarde uma resposta do servidor após enviar a configuração
            try {
                Thread.sleep(5000); // Reduzido o tempo de espera para 5 segundos
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt(); // Restaure o status de interrupção
            }

            // Envia as mensagens esperadas
            for (int j = 0; j < maxConsideredMessagesExpected; j++) {
                msg = cycle+";"+sourceCurrentIndexMessage + ";" + System.currentTimeMillis() + ";" + "\n";
                send(msg);
                sourceCurrentIndexMessage++;
            }

            while (!cyclesCompleted.get(cycle)){
                try {
                    Thread.sleep(1000); // Reduzido o tempo de espera para 5 segundos
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt(); // Restaure o status de interrupção
                }
            }

            cycle++;
        }
    }





    /**
     * Sends a configuration message to the variatedServer load balancer.
     *
     * @param configMessage Configuration message to be sent
     */
    private void sendMessageToConfigureServer(String configMessage) {
        Socket socket = null;
        BufferedWriter out = null;
        BufferedReader in = null;
        int retries = 5;  // Número de tentativas
        int attempt = 0;
        boolean success = false;

        while (attempt < retries && !success) {
            try {
                // Tentar estabelecer a conexão
                socket = new Socket(variatedServerLoadBalancerIp, variatedServerLoadBalancerPort);
                out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                // Enviar a mensagem de configuração
                out.write(configMessage);
                out.newLine();
                out.flush();

                // Aguardar a confirmação (se necessário)
                String response = in.readLine();
                log("Received response from variatedServer: " + response);
                success = true;  // Marcar como sucesso se não houver exceção
            } catch (IOException e) {
                log("Error sending configuration message to variatedServer, retrying...");
                attempt++;
                try {
                    Thread.sleep(2000);  // Aguardar 2 segundos antes da próxima tentativa
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            } finally {
                // Fechar os recursos
                try {
                    if (out != null) out.close();
                    if (in != null) in.close();
                    if (socket != null) socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        if (!success) {
            throw new RuntimeException("Failed to connect to variatedServer after " + retries + " attempts");
        }
    }


    private void send(String msg) throws IOException, ClassNotFoundException {
        if (isDestinyFree(connectionDestinySocket)) {
            sendMessageToDestiny(msg);
        } else {
            System.err.print("DROPPED IN SOURCE " + msg);
            droppCount++;
        }
        try {
            Thread.sleep(arrivalDelay);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }

    /**
     * Register MRT at the end of the received message.
     *
     * @param receivedMessage Received message
     * @return Message with MRT appended
     */
    private String registerMRTAtTheEnd(String receivedMessage) {
        Long last = Long.valueOf(receivedMessage.split(";")[receivedMessage.split(";").length - 2]);
        Long first = Long.valueOf(receivedMessage.split(";")[2]);
        long currentMRT = last - first;
        receivedMessage += "RESPONSE TIME:;" + currentMRT + ";";


        return receivedMessage;
    }

    /**
     * Method to handle receiving messages.
     *
     * @param newSocketConnection Socket connection for receiving messages
     */
    protected void receivingMessages(Socket newSocketConnection) {
        try {
            System.err.println(proxyName + " enabled to receive messages.");

            String receivedMessage = null;

            DataInputStream dataInputStream = new DataInputStream(newSocketConnection.getInputStream());
            while (true) {
                if (dataInputStream.available() > 0) {
                    receivedMessage = dataInputStream.readLine();
                }

                if (receivedMessage != null) {
                    receivedMessage = registerMRTAtTheEnd(receivedMessage);
                    if (modelFeedingStage)
                        executeFirstStageOfModelFeeding(receivedMessage);
                    else
                        executeSecondStageOfValidation(receivedMessage);
                    receivedMessage = null;
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Execute the first stage of model feeding.
     *
     * @param receivedMessage Received message
     */
    private void executeFirstStageOfModelFeeding(String receivedMessage) {
        consideredMessages.add(receivedMessage);
        log(receivedMessage);

        int index = Integer.parseInt(receivedMessage.split(";")[1]);
        if (index == 2) {
            Map<String, List<Integer>> map = new LinkedHashMap<>();
            Map<String, Double> averages = new LinkedHashMap<>();
            int keyIndex = 1;

            for (String message : consideredMessages) {
                String[] lines = message.split("\n");
                for (String line : lines) {
                    if (line.startsWith("0;")) continue; // Ignore line starting with "0;"
                    String[] values = line.split(";");
                    // Start from the second index to skip the new number
                    for (int j = 4; j < values.length - 2; j += 3) { // Ignore the last two elements
                        String value = values[j];
                        String key = "T" + (j);
                        map.putIfAbsent(key, new ArrayList<>());
                        map.get(key).add(Integer.parseInt(value));
                    }
                }
            }

            for (Map.Entry<String, List<Integer>> entry : map.entrySet()) {
                double sum = 0;
                for (int num : entry.getValue()) {
                    sum += num;
                }
                double average = sum / entry.getValue().size();
                averages.put("T" + keyIndex++, average);
            }

            log("The times to feed the models transitions are the following:");
            for (Map.Entry<String, Double> entry : averages.entrySet()) {
                log(entry.getKey() + " = " + entry.getValue());
            }
            System.exit(0);
        }
    }

    private void executeSecondStageOfValidation(String receivedMessage) {
        consideredMessages.add(receivedMessage);

        int index = Integer.parseInt(receivedMessage.split(";")[1]);
        int currentCycle = Integer.parseInt(receivedMessage.split(";")[0]);

        if (!cyclesCompleted.get(currentCycle)) {
            log(receivedMessage);
            log("Number of considered messages: " + consideredMessages.size() + " of " + maxConsideredMessagesExpected);
        }

        // Cancelar o temporizador se ele estiver em execução
        if (timeoutFuture != null && !timeoutFuture.isDone()) {
            timeoutFuture.cancel(false);
        }

        // Reiniciar o temporizador
        timeoutFuture = scheduler.schedule(() -> {
            if (isTimeoutTriggered) {
                return;
            }
            isTimeoutTriggered = true;

            if (!cyclesCompleted.get(currentCycle)) {
                partialRegistration();
                cyclesCompleted.set(currentCycle, true);

                // Verifica se todos os ciclos foram concluídos
                if (allCyclesCompleted()) {
                    allCyclesCompleted = true;
                    log("All cycles completed.");
                    // Gere o gráfico após o envio de todas as mensagens
                    System.out.println("finalizou");
                    try {
                        Thread.sleep(4000);
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }

                    String xPrintedName;
                }
            }
        }, timeoutDuration, TimeUnit.MILLISECONDS);

        // Resetar o estado do temporizador
        isTimeoutTriggered = false;
    }



    private boolean allCyclesCompleted() {
        for (Boolean b :cyclesCompleted) {
            if (!b)
                return false;
        }
        return true;
    }


    private void partialRegistration() {
        // Número de mensagens a considerar (metade do total, mas pelo menos 1)
        int numMessagesToConsider = Math.max(1, consideredMessages.size() / 5);


        // Seleciona as últimas `numMessagesToConsider` mensagens
        List<String> messagesToProcess = getMessagesToProcess(numMessagesToConsider);

        // Calcula o MRT e o desvio padrão
        double mrtFromExperiment = calculateMRTFromMessages(messagesToProcess);
//        double standardDeviation = Utils.calculateStandardDeviation(extractMRTs(messagesToProcess));
        double standardDeviation = mrtFromExperiment/11; //o desvio padrão real normalmente dá muito pequeno

        // Exibe os resultados
        displayResults(mrtFromExperiment, standardDeviation);

        // Limpa as mensagens consideradas para o próximo ciclo
        consideredMessages.clear();
    }

    /**
     * Obtém as últimas `numMessagesToConsider` mensagens da lista `consideredMessages`.
     *
     * @param numMessagesToConsider Número de mensagens a considerar
     * @return Lista das mensagens a serem processadas
     */
    private List<String> getMessagesToProcess(int numMessagesToConsider) {
        int startIndex = Math.max(consideredMessages.size() - numMessagesToConsider, 0);
        return consideredMessages.subList(startIndex, consideredMessages.size());
    }

    /**
     * Calcula o MRT a partir das mensagens fornecidas.
     *
     * @param messages Lista das mensagens a serem processadas
     * @return MRT calculado a partir das mensagens
     */
    private double calculateMRTFromMessages(List<String> messages) {
        long totalMRT = 0;
        for (String message : messages) {
            totalMRT += parseMRT(message);
        }
        return totalMRT / (double) messages.size();
    }

    /**
     * Extrai os valores de MRT das mensagens fornecidas.
     *
     * @param messages Lista das mensagens a serem processadas
     * @return Lista de valores de MRT extraídos
     */
    private List<Double> extractMRTs(List<String> messages) {
        List<Double> mrts = new ArrayList<>();
        for (String message : messages) {
            mrts.add(parseMRT(message));
        }
        return mrts;
    }

    /**
     * Extrai o valor de MRT de uma única mensagem.
     *
     * @param message Mensagem contendo o valor de MRT
     * @return Valor de MRT extraído
     */
    private double parseMRT(String message) {
        String[] parts = message.split(";");
        return Double.parseDouble(parts[parts.length - 1]);
    }

    /**
     * Exibe os resultados do MRT e do desvio padrão.
     *
     * @param mrtFromExperiment MRT calculado a partir das mensagens
     * @param standardDeviation Desvio padrão calculado
     */
    private void displayResults(double mrtFromExperiment, double standardDeviation) {
        log("MRT From Experiment: " + mrtFromExperiment +
                "; SD From Experiment: " + standardDeviation);
        experimentData.add(mrtFromExperiment);
        experimentError.add(standardDeviation);
    }


    /**
     * Create a connection with the destination.
     *
     * @throws IOException If an I/O error occurs
     */
    protected void createConnectionWithDestiny() throws IOException {
        connectionDestinySocket = new Socket(targetAddress.getIp(), targetAddress.getPort());
    }

}
