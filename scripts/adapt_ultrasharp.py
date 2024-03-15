import argparse
import torch


def convert_key_names(old_keys):
    new_keys = {}
    for key in old_keys:
        new_key = key.replace('model.0', 'conv_first').replace('model.1.sub.', 'body.'). \
            replace('RDB', 'rdb').replace('.0.weight', '.weight').replace('.0.bias', '.bias'). \
            replace('model.10', 'conv_last').replace('model.8', 'conv_hr'). \
            replace('model.6', 'conv_up2').replace('model.3','conv_up1').replace('body.23','conv_body')
        new_keys[key] = new_key
    return new_keys

def main(args):
    # Load the model with incompatible keys
    state_dict = torch.load(args.input)

    # Convert the key names
    new_state_dict = {}
    key_mapping = convert_key_names(state_dict.keys())
    for old_key, new_key in key_mapping.items():
        new_state_dict[new_key] = state_dict[old_key]

    # Create a new dictionary with the 'params_ema' key
    new_state_dict = {'params_ema': new_state_dict}

    # Save the modified model
    torch.save(new_state_dict, args.output)


if __name__ == '__main__':
    """Convert 4x-UltraSharp model to a compatible format. May work for other models as well."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', type=str, default='experiments/pretrained_models/4x-UltraSharp.pth', help='Input model path')
    parser.add_argument('--output', type=str, default='weights/UltraSharp_4x.pth', help='Output model path')
    args = parser.parse_args()

    main(args)