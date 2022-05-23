import pandas as pd
import matplotlib.pyplot as plt


def k_to_decimal(num: str):
    if isinstance(num, str) and num[-1] == 'k':
        return float(num[:-1]) * 1000
    else:
        return float(num)


def s_to_decimal(num: str):
    if isinstance(num, str) and num[-1] == 's':
        return float(num[:-1])
    else:
        return float(num)


def main():
    # generate the two csv files by running `openssl speed [type]`
    # once for aes -> aes.csv
    # once for rsa -> rsa.csv


    # read the inputs in
    with open('input/aes.csv', 'r') as f:
        aes_df = pd.read_csv(f)
    for col in aes_df.columns[1:]:
        aes_df[col] = aes_df[col].apply(k_to_decimal)

    with open('input/rsa.csv', 'r') as f:
        rsa_df = pd.read_csv(f)
    rsa_df['sign/s'] = rsa_df['sign/s'].apply(float)
    rsa_df['verify/s'] = rsa_df['verify/s'].apply(float)

    figure, axis = plt.subplots(1, 2)
    aes_axis, rsa_axis = axis

    # plot aes data
    for _, row in aes_df.iterrows():
        aes_axis.plot(row.values[1:], row.index[1:], label=row.values[0])
    aes_axis.set_xlabel('Throughput (bits/s)')
    aes_axis.set_ylabel('Block size')
    aes_axis.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                    mode="expand", borderaxespad=0, ncol=3)
    
    # plot rsa data
    rsa_axis.plot('sign/s', 'type', data=rsa_df, label='sign')
    rsa_axis.plot('verify/s', 'type', data=rsa_df, label='verify')
    rsa_axis.set_xlabel('Throughput (bits/s)')
    rsa_axis.set_ylabel('Key size')
    rsa_axis.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                    mode="expand", borderaxespad=0, ncol=3)

    plt.show()


if __name__ == "__main__":
    main()