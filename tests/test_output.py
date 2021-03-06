"Test facemap pipeline by comparing outputs"
from facemap import process
import numpy as np
from pathlib import Path
import os

r_tol, a_tol = 1e-2, 1e-2

def test_output_single_video(data_dir, video_names):
    clear_output(data_dir, video_names)
    v1, _ = video_names
    test_filenames = [[str(data_dir.joinpath('data').joinpath('cam1').joinpath(v1))]] # [[data_dir+video for video in v1]]
    save_path = str(data_dir.joinpath('data').joinpath('cam1'))
    process.run(test_filenames, movSVD=True, savepath=save_path)    

    output_filename, _ = os.path.splitext(v1[0])
    test_proc_filename = save_path.joinpath(output_filename+"_proc.npy")
    output = np.load(test_proc_filename,allow_pickle=True).item()
    expected_proc_filename = os.getcwd()+"/tests/expected_output/singlevideo_proc.npy"
    expected_output = np.load(expected_proc_filename,allow_pickle=True).item()
    clear_output(data_dir, video_names)

    assert is_output_correct(output, expected_output)

def test_output_multivideo(data_dir, video_names):
    clear_output(data_dir, video_names)
    v1, v2 = video_names
    test1 = str(data_dir.joinpath('data').joinpath('cam1').joinpath(v1))#os.path.join(data_dir,v1[0])
    test2 = str(data_dir.joinpath('data').joinpath('cam2').joinpath(v2))#os.path.join(data_dir,v2[0])
    # For videos recorded simultaneously from multiple cams
    test_filenames = [[test1, test2]]
    save_path = str(data_dir.joinpath('data').joinpath('cam2'))
    process.run(test_filenames, movSVD=True, savepath=save_path)    

    output_filename, _ = os.path.splitext(v2[0])
    test_proc_filename = save_path.joinpath(output_filename+"_proc.npy")
    output = np.load(test_proc_filename,allow_pickle=True).item()
    expected_proc_filename = os.getcwd()+"/tests/expected_output/multivideo_proc.npy"
    expected_output = np.load(expected_proc_filename,allow_pickle=True).item()
    clear_output(data_dir, video_names)

    assert is_output_correct(output, expected_output)

def is_output_correct(test_output, expected_output):
    params_match = check_params(test_output, expected_output)
    frames_match = check_frames(test_output, expected_output)
    motion_match = check_motion(test_output, expected_output)
    U_match = check_U(test_output, expected_output)
    V_match = check_V(test_output, expected_output)
    return params_match and frames_match and motion_match and U_match and V_match

def check_params(test_output, expected_output):
    all_outputs_match = (test_output['Ly'] == expected_output['Ly'] and
                    test_output['Lx'] == expected_output['Lx'] and
                    test_output['sbin'] ==  expected_output['sbin'] and
                    test_output['Lybin'][0] ==  expected_output['Lybin'][0] and
                    test_output['Lxbin'][0] == expected_output['Lxbin'][0] and 
                    test_output['sybin'][0] == expected_output['sybin'][0] and
                    test_output['sxbin'][0] == expected_output['sxbin'][0] and
                    test_output['LYbin'] == expected_output['LYbin'] and
                    test_output['LXbin'] == expected_output['LXbin']) 
    return all_outputs_match

def check_frames(test_output, expected_output):
    print(test_output['avgframe'][0].shape, expected_output['avgframe'][0].shape)
    avgframes_match = np.allclose(test_output['avgframe'][0], expected_output['avgframe'][0], 
                        rtol=r_tol, atol=a_tol) 
    avgmotion_match = np.allclose(test_output['avgmotion'][0], expected_output['avgmotion'][0], 
                        rtol=r_tol, atol=a_tol) 
    avgframe_reshape_match = np.allclose(test_output['avgframe_reshape'][0], expected_output['avgframe_reshape'][0], 
                        rtol=r_tol, atol=a_tol)
    avgmotion_reshape_match = np.allclose(test_output['avgmotion_reshape'][0], expected_output['avgmotion_reshape'][0], 
                        rtol=r_tol, atol=a_tol)         
    return avgframes_match and avgmotion_match and avgframe_reshape_match and avgmotion_reshape_match

def check_U(test_output, expected_output):
    motionMask = np.allclose(test_output['motMask'][0], expected_output['motMask'][0], rtol=r_tol, atol=a_tol)
    movieMask = np.allclose(test_output['movMask'][0], expected_output['movMask'][0], rtol=r_tol, atol=a_tol)
    motionMask_reshape = np.allclose(test_output['motMask_reshape'][0], expected_output['motMask_reshape'][0], rtol=r_tol, atol=a_tol)
    movMask_reshape = np.allclose(test_output['movMask_reshape'][0], expected_output['movMask_reshape'][0], rtol=r_tol, atol=a_tol)
    return motionMask and movieMask and motionMask_reshape and movMask_reshape

def check_V(test_output, expected_output):
    motion_V = np.allclose(test_output['motSVD'][0], expected_output['motSVD'][0], rtol=r_tol, atol=a_tol)
    movie_V = np.allclose(test_output['movSVD'][0], expected_output['movSVD'][0], rtol=r_tol, atol=a_tol)
    return motion_V and movie_V

def check_motion(test_output, expected_output):
    return (test_output['motion'][0] == expected_output['motion'][0]).all()

def clear_output(data_dir, video_names):
    data_dir_cam1 = data_dir.joinpath('cam1')
    data_dir_cam2 = data_dir.joinpath('cam2')
    for video_name in video_names:
        if '1' in video_name:
            cached_file = str(data_dir_cam1.joinpath(video_name))
            name, ext = os.path.splitext(cached_file)
            output = name + '_proc.npy'
        else:
            cached_file = str(data_dir_cam2.joinpath(video_name))
            name, ext = os.path.splitext(cached_file)
            output = name + '_proc.npy'
        if os.path.exists(output):
            os.remove(output)
