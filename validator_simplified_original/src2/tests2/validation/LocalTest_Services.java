package tests.validation;


import domain.LoadBalancerProxy;
import domain.Source;

/**
 * Estes estudos de caso são apenas ilustrativos e de testes.
 * Estes estudos de caso não devem ser executados da maneira que está aqui (monolítico).
 * Você deve executar os componentes separadamente de forma distribuída em máquinas vísicas ou VMs e contêineres.
 *  *  @author Airton
 */
public class LocalTest_Services {

	public static void main(String[] args) {
		executeStage();
	}

	private static void executeStage() {

		String path = System.getProperty("user.dir") + "/"+ "src/tests/validation/";
		String loadBalancerJsonPath1 = path + "loadbalancer1.properties";
		String loadBalancerJsonPath2 = path + "loadbalancer2.properties";

		new LoadBalancerProxy(loadBalancerJsonPath2).start();

		new LoadBalancerProxy(loadBalancerJsonPath1).start();

		new Source(path).start();
	}
}

