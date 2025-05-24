package domain;




import domain.utils.Utils;

import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.*;

/**
 * Recebe requisições do Source ou de um service de outro loadbalancer e faz o balanceamento de requisições para seus services respectivos.
 *  @author Airton
 */
public class LoadBalancerProxy extends AbstractProxy {



	List <TargetAddress> serviceAddresses = new ArrayList<>();

	Integer queueLoadBalancerMaxSize;

	List<String> queue = new ArrayList<>();

	List<Socket> connectionDestinySockets = new ArrayList<>();

	List<Integer> qtdServicesList;

	int indexCurrentQtdServices;


	double serviceTime;

	double serviceTimeStandartDeviation;

	boolean targetIsSource;

	String serviceTargetIp;

	int serviceTargetPort;

	List<ServiceProxy> services = new ArrayList<>();

	Set<String> sentConfigMessages = new HashSet<>();

	public static void main(String[] args) throws IOException {
		LoadBalancerProxy loadBalancerProxy = new LoadBalancerProxy();
		loadBalancerProxy.start();
	}


	public LoadBalancerProxy(String configPath) {
		Properties props = new Properties();
		try (FileInputStream fis = new FileInputStream(configPath)) {
			props.load(fis);
		} catch (IOException e) {
			throw new RuntimeException("Error reading properties file", e);
		}

		// Carregar parâmetros diretamente das propriedades
		this.proxyName = props.getProperty("server.loadBalancerName");
		this.localPort = Integer.parseInt(props.getProperty("server.loadBalancerPort"));
		this.queueLoadBalancerMaxSize = Integer.parseInt(props.getProperty("server.queueLoadBalancerMaxSize"));
		this.qtdServicesList = new ArrayList<>(Collections.singletonList(Integer.parseInt(props.getProperty("server.qtdServices"))));

		serviceTargetIp = props.getProperty("service.serviceTargetIp");
		serviceTargetPort = Integer.parseInt(props.getProperty("service.serviceTargetPort"));
		serviceTime = Double.parseDouble(props.getProperty("service.serviceTime"));
		serviceTimeStandartDeviation = Double.parseDouble(props.getProperty("service.std"));
		targetIsSource = Boolean.parseBoolean(props.getProperty("service.targetIsSource"));

		this.serviceAddresses = createServices(
				this.localPort,
				serviceTargetPort,
				serviceTime,
				serviceTargetIp,
				targetIsSource,
				serviceTimeStandartDeviation
		);

		this.targetAddress = serviceAddresses.get(0);


		printLoadBalancerParameters();
	}

	public void printLoadBalancerParameters() {
		System.out.println("======================================");
		System.out.println("Load Balancer Parameters:");

		System.out.println("Load Balancer Name: " + this.proxyName);
		System.out.println("Local Port: " + this.localPort);
		System.out.println("Queue Load Balancer Max Size: " + this.queueLoadBalancerMaxSize);
		System.out.println("Qtd Services List: " + this.qtdServicesList);


		System.out.println("======================================");
	}


	/**
	 * Constructor to initialize Load Balancer Proxy using configuration from loadbalancer_01.json.
	 */
	public LoadBalancerProxy() {
		this(System.getProperty("user.dir")+"/loadbalancer.properties");
	}


	private List<TargetAddress> createServices(int loadBalancerPort, int targetPort, double serviceTime, String targetIp, boolean targetIsSource, double std) {
		List<TargetAddress> serviceAddresses = new ArrayList<>();
		Integer port = loadBalancerPort+1;
		indexCurrentQtdServices = 0;
		int qtdServicesInthisCicle = qtdServicesList.get(0);
		while (qtdServicesInthisCicle > 0) {
			TargetAddress ta = new TargetAddress("localhost", port);
			ServiceProxy serviceProxy = new ServiceProxy("service" + port, port, new TargetAddress(targetIp, targetPort), serviceTime, std, targetIsSource);
			this.services.add(serviceProxy);
			serviceProxy.start();
			serviceAddresses.add(ta);

			port++;
			qtdServicesInthisCicle--;
		}

		return serviceAddresses;
	}



	@Override
	public void createConnectionWithDestiny() throws IOException {
		for (TargetAddress targetAddress: serviceAddresses) {
			connectionDestinySockets.add(new Socket(targetAddress.getIp(),targetAddress.getPort()));
		}
	}

	@Override
	public synchronized boolean hasSomethingToProcess() {
		return !this.queue.isEmpty();
	}

	public void run() {
		try {
			new ConnectionEstablishmentOriginThread().start();
			new ConnectionEstablishmentDestinyThread().start();
			System.out.println("Starting " + proxyName);

			String msg;
			while (true) {

				if (hasSomethingToProcess()) {

					boolean notSentYet = true;
					while (notSentYet) {
						for (Socket socket : connectionDestinySockets) {
							if (isDestinyFree(socket)) {
								msg = queue.remove(0);
								sendMessageToDestiny(msg, socket);
								notSentYet = false;
								break;
							}
						}
					}

				}
			}
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		catch (ClassNotFoundException e) {
			throw new RuntimeException(e);
		}
	}

	@Override
	protected void receivingMessages(Socket socket) throws IOException {
		String receivedMessage = null;

		System.err.println(proxyName + " enabled to receive messages.");

		DataInputStream dataInputStream = new DataInputStream(socket.getInputStream());
		while (true) {
			if (dataInputStream.available() > 0) {
				receivedMessage = dataInputStream.readLine();
			}
			if (receivedMessage != null && !receivedMessage.isEmpty()) {
				if (receivedMessage.contains("config")) {
					changeServiceTargetsOfThisServer(receivedMessage, socket);
				} else if (receivedMessage.equals("ping")) {
					handlePingMessage(socket);
				} else {
					handleMessage(receivedMessage);
				}
			} else {
//				System.err.println("Received empty or null message: " + receivedMessage);
//				System.exit(0);
			}

			receivedMessage = null; // Reiniciar a variável para a próxima iteração
		}
	}





	private void handlePingMessage(Socket socket) throws IOException {
		ObjectOutputStream oos = new ObjectOutputStream(socket.getOutputStream());
		if (this.queue.size() < queueLoadBalancerMaxSize) {
			oos.writeObject("free");
		} else {
			oos.writeObject("busy");
		}
	}

	private void handleMessage(String receivedMessage) {
		receivedMessage = Utils.registerTime(receivedMessage);
		receivedMessage += System.currentTimeMillis() + ";" + "\n";
		this.queue.add(receivedMessage);
	}
	private synchronized void changeServiceTargetsOfThisServer(String receivedMessage, Socket socket) {
		String[] parts = receivedMessage.split(";");
		// Clear existing services and stop them
		Iterator<ServiceProxy> iterator = services.iterator();
		while (iterator.hasNext()) {
			ServiceProxy serviceProxy = iterator.next();
			serviceProxy.stopService();
			iterator.remove(); // Use iterator's remove method to safely remove from list
		}

		// Clear existing service addresses
		serviceAddresses.clear();

		// Update service addresses with new targets
		this.indexCurrentQtdServices++;
		int qtdServicesInthisCycle = Integer.parseInt(parts[1]);

		for (int i = 0; i < qtdServicesInthisCycle; i++) {
			int servicePort = getRandomNumber();
//			ServiceProxy serviceProxy = new ServiceProxy(serverSettings);

			ServiceProxy serviceProxy = new ServiceProxy(
					"service" + servicePort, // Nome do serviço
					servicePort, // Porta do serviço
					new TargetAddress(serviceTargetIp,serviceTargetPort), // Endereço de destino
					serviceTime, // Tempo de serviço, substitua este valor conforme necessário
					serviceTimeStandartDeviation, // Desvio padrão (std), substitua este valor conforme necessário
					targetIsSource // targetIsSource, ajuste conforme necessário
			);

			serviceProxy.start();
			services.add(serviceProxy);

			TargetAddress ta = new TargetAddress("localhost", servicePort);
			serviceAddresses.add(ta);
		}

		// Update target address to the first one in the new list
		targetAddress = serviceAddresses.get(0);


		// Introduce a delay before reconnecting (optional)
		try {
			Thread.sleep(2000); // Wait for  before reconnecting
			// Recreate connections with the new targets
			createConnectionWithDestiny();
			Thread.sleep(2000); // Wait for  before reconnecting
			ObjectOutputStream oos = new ObjectOutputStream(socket.getOutputStream());
			oos.writeObject("Configuration has finished\n");
		} catch (InterruptedException | IOException e) {
			throw new RuntimeException(e);
		}
	}


	// Method to generate random number between 1000 and 9000
	public static int getRandomNumber() {
		Random random = new Random();
		return random.nextInt(9000 - 1000 + 1) + 1000;
	}



}
