package domain.utils;

public enum VariatedParameter {
    SERVICES("Services"),
    AR("AR");

    private String value;

    VariatedParameter(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    public static VariatedParameter fromValue(String value) {
        for (VariatedParameter param : VariatedParameter.values()) {
            if (param.value.equalsIgnoreCase(value)) {
                return param;
            }
        }
        throw new IllegalArgumentException("Invalid variatedParameter value: " + value);
    }
}